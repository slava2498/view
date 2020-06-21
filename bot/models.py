from django.db import models
from django.shortcuts import reverse
from datetime import datetime
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete, m2m_changed
import telebot
from telebot import TeleBot, types
import logging
import math
from astudy.settings import ASTUDY_TOKEN, CABINET_TOKEN, CABINET_START, font

astudy = telebot.TeleBot(ASTUDY_TOKEN)
cabinet = telebot.TeleBot(CABINET_TOKEN)

ROLE = (
    ('customer', 'Заказчик'),
    ('executor', 'Исполнитель'),
)
TYPE_GRADE = (
    ('one', 'Качество'),
    ('two', 'Скорость'),
    ('three', 'Оформление'),
    ('four', 'Вежливость'),
)

class CommonInfo(models.Model):
	date_add = models.DateTimeField(verbose_name="Дата добавления", auto_now_add=True)
	date_change = models.DateTimeField(verbose_name="Дата изменения", auto_now=True)

	class Meta:
		abstract = True

class Subject(CommonInfo):
	name = models.CharField(verbose_name="Имя", max_length=100, blank=True, null=True)
	next_subject = models.ManyToManyField('Subject',  verbose_name="Следующие предметы", blank=True, null=True)
	level = models.IntegerField(verbose_name="Уровень", default=1)

	class Meta:
		verbose_name = "Темы"
		verbose_name_plural = "Темы"

	def __str__(self):
		parent = Subject.objects.filter(next_subject__pk=self.id)
		if(parent): parent = '| Уже выбрано в ' + parent[0].name
		else: parent = ''
		return '№{} {}, уровень {} {}'.format(self.id, self.name, self.level, parent)

class Files(CommonInfo):
	upload = models.FileField(upload_to='uploads/')

	def __str__(self):
		return '{}.{}'.format(str(self.id), self.upload)

class Clients(CommonInfo):
	refer = models.ForeignKey('Clients', on_delete=models.SET_NULL,
    							verbose_name="Рефер", blank=True, null=True)
	refer_code = models.CharField(verbose_name="Реферальный код", max_length=255, default='')
	chat_id = models.CharField(verbose_name="chat_id", max_length=100)
	name = models.CharField(verbose_name="Имя", max_length=100, blank=True, null=True)
	city = models.CharField(verbose_name="Город", max_length=100, blank=True, null=True)
	more = models.CharField(verbose_name="Подробнее", max_length=299, blank=True, null=True)
	filter_subjects = models.ManyToManyField(Subject,  verbose_name="Предметы", blank=True, null=True)
	balance = models.FloatField(verbose_name="Баланс", default=0)
	withdraw = models.TextField(verbose_name="Куда выводить средства", max_length=255, blank=True, null=True)

	bonuse = models.BooleanField(verbose_name="Использовать бонус", default=False)

	class Meta:
		verbose_name = "Карточку пользователя"
		verbose_name_plural = "Карточки пользователей"

	def __str__(self):
		return '{}.{}'.format(self.id, self.chat_id)

@receiver(post_save, sender=Clients)
def refer_client(sender, **kwargs):
	instance = kwargs['instance']
	print(instance)
	if(kwargs['update_fields']): 
		if('refer' in kwargs['update_fields']):
			client = instance
			text = 'По вашему реферальному коду зарегистрировался пользователь №{}'.format(client.id)
			astudy.send_message(chat_id=client.refer.chat_id, text=text, parse_mode="HTML")



class Tasks(CommonInfo):
	client = models.ForeignKey(Clients, on_delete=models.CASCADE,
								verbose_name="Заказчик", related_name='customer')
	executor = models.ForeignKey(Clients, on_delete=models.CASCADE,
								verbose_name="Исполнитель", related_name='executor', blank=True, null=True)
	subject = models.ForeignKey(Subject, on_delete=models.CASCADE,
								verbose_name="Тема")
	deadline = models.DateTimeField(verbose_name="Дата сдачи", blank=True, null=True)
	files = models.ManyToManyField(Files,  verbose_name="Файлы", blank=True, null=True)
	more = models.TextField(verbose_name="Описание задачи", max_length=255, blank=True, null=True)
	created = models.BooleanField(verbose_name="Создана", default=False)

	state = models.BooleanField(verbose_name="Подтверждается исполнителем", default=False)
	finish = models.BooleanField(verbose_name="Выполнена", default=False)

	price_one = models.FloatField(verbose_name="Цена без комиссии заказчика", default=0)
	price_two = models.FloatField(verbose_name="Цена с комиссией заказчика", default=0)

	class Meta:
		verbose_name = "Задачи"
		verbose_name_plural = "Задачи"

	def __str__(self):
		return '{}.{} {}'.format(self.id, self.client, self.subject.name)

@receiver(post_save, sender=Tasks)
def update_task(sender, **kwargs):
	instance = kwargs['instance']
	print(instance)
	if(kwargs['update_fields']): 
		if('created' in kwargs['update_fields']):
			task = instance
			subject = task.subject
			clients = Clients.objects.filter(filter_subjects=subject).exclude(id=instance.client.id)
			keyboard = types.InlineKeyboardMarkup(True)
			keyboard.keyboard.append([{'text': 'Подробнее', 'callback_data': 'EXECUTOR100_' + str(task.id)}])
			text = '💣 Новый заказ: {} ({})'.format(font('bold', '#{} {}'.format(task.id, task.subject.name)), (task.more[:20] + '...') if len(task.more) > 20 else task.more)
			for x in clients:
				try:
					astudy.send_message(chat_id=x.chat_id, text=text, reply_markup=keyboard, parse_mode="HTML")
				except:
					pass

		elif('more' in kwargs['update_fields']):
			task = instance
			subject = task.subject
			feedbacks = Feedback.objects.filter(task=task)
			if('more' in kwargs['update_fields']):
				text = '⚠️ Заказчик изменил описание заказа {}\nВаша заявка ануллирована, просим ознакомиться'.format(font('bold', '#{} {}'.format(task.id, task.subject.name)))

			keyboard = types.InlineKeyboardMarkup(True)
			keyboard.keyboard.append([{'text': 'Подробнее', 'callback_data': 'EXECUTOR100_' + str(task.id)}])
			for x in feedbacks:
				astudy.send_message(chat_id=x.client.chat_id, text=text, reply_markup=keyboard, parse_mode="HTML")

			feedbacks.delete()

		elif('executor' in kwargs['update_fields'] and instance.executor is not None):
			task = instance
			keyboard = types.InlineKeyboardMarkup(True)
			buttons = []
			# keyboard.keyboard.append([{'text': 'Подробнее', 'callback_data': 'EXECUTOR150_' + str(task.id) + '_____'}])
			buttons.append({'text': 'Да ✅', 'callback_data': 'EXECUTOR160_' + str(task.id) + '_yes____'})
			buttons.append({'text': 'Нет ❌', 'callback_data': 'EXECUTOR160_' + str(task.id) + '_no____'})
			f = lambda A, n: [A[i:i+n] for i in range(0, len(A), n)]
			keyboard.keyboard = f(buttons, 1)
			text = '✅ Вас выбрали помощником на заказ {}\n'.format(font('bold', '#{}-{}'.format(task.id, task.subject.name)))
			text += str(font('light', 'Вы подтверждаете начало выполнения?'))
			astudy.send_message(chat_id=task.executor.chat_id, text=text, reply_markup=keyboard, parse_mode="HTML")

		elif('finish' in kwargs['update_fields']):
			task = instance
			executor = Clients.objects.filter(id=instance.executor.id)[0]
			feedback = Feedback.objects.filter(task=task, client=executor)[0]
			price_executor = feedback.price_one
			if(task.client.refer):
				refer = Clients.objects.filter(id=task.client.refer.id)[0]
				comission = Commissions.objects.filter()[0]
				price_refer = task.price_two - task.price_two * comission.amount_three
				refer.balance = price_refer
				refer.save(update_fields=['balance'])
				cabinet.send_message(chat_id=refer.chat_id, text='Реферальные начисления: {} грн.'.format(math.ceil(price_executor)), parse_mode="HTML")

			executor.balance += price_executor
			executor.save(update_fields=['balance'])
			text = font('bold', 'Поздравляем 🎉🎉🎉 с успешным выполнением заказа, ') + 'ваш баланс пополнен на {}\n'.format(font('bold', '{} грн.'.format(math.ceil(price_executor))))
			text += 'Мы рады, что вы зарабатываете вместе с нами! '
			text += font('light', 'Если у вас есть предложения или идеи, как улучшить сервис, пишите @Viktor_Rachuk')
			cabinet.send_message(chat_id=instance.executor.chat_id, text=text, parse_mode="HTML")

			keyboard_customer = types.InlineKeyboardMarkup(True)
			keyboard_executor = types.InlineKeyboardMarkup(True)
			star = '⭐️'
			cabinet_customer = Cabinet.objects.filter(task=task, role='customer')[0]
			cabinet_executor = Cabinet.objects.filter(task=task, role='executor')[0]
			for x in range(5):
				# keyboard_customer.keyboard.append([{'text': star, 'callback_data': 'CABINET121_' + str(cabinet_customer.id) + '_customer_' + str(x)}])
				keyboard_executor.keyboard.append([{'text': star, 'callback_data': 'CABINET121_' + str(cabinet_executor.id) + '_executor_' + str(x)}])
				star += '⭐️'

			answer = 'Оцените ' + font('bold', 'качество работы')
			cabinet.send_message(chat_id=instance.client.chat_id, text=answer, reply_markup=keyboard_executor, parse_mode="HTML")
			# cabinet.send_message(chat_id=instance.executor.chat_id, text=answer, reply_markup=keyboard_customer)

def toppings_changed(sender, **kwargs):
	task = kwargs['instance']
	subject = task.subject
	text = '⚠️ Заказчик изменил файлы к задаче {}\nВаша заявка ануллирована, просим ознакомиться'.format(font('bold', '#{} {}'.format(task.id, task.subject.name)))
	keyboard = types.InlineKeyboardMarkup(True)
	keyboard.keyboard.append([{'text': 'Подробнее', 'callback_data': 'EXECUTOR100_' + str(task.id)}])
	feedbacks = Feedback.objects.filter(task=task)
	for x in feedbacks:
		astudy.send_message(chat_id=x.client.chat_id, text=text, reply_markup=keyboard, parse_mode="HTML")

	feedbacks.delete()

m2m_changed.connect(toppings_changed, sender=Tasks.files.through)

@receiver(pre_delete, sender=Tasks)
def delete_model(sender, **kwargs):
	task = kwargs['instance']
	subject = task.subject
	clients = Feedback.objects.filter(task=task)
	text = 'Заказчик удалил заказ {}\n'.format(font('bold', '#{} {}'.format(task.id, subject.name)))
	for x in clients:
		if(task.client.id != x.id):
			try:
				astudy.send_message(chat_id=x.client.chat_id, text=text, parse_mode="HTML")
			except:
				pass

class Feedback(CommonInfo):
	client = models.ForeignKey(Clients, on_delete=models.CASCADE,
								verbose_name="Пользователь")
	task = models.ForeignKey(Tasks, on_delete=models.CASCADE,
								verbose_name="Задача")
	question = models.TextField(verbose_name="Вопрос", max_length=255, blank=True, null=True)
	price_one = models.FloatField(verbose_name="Цена без комиссии исполнителя", default=0)
	price_two = models.FloatField(verbose_name="Цена с комиссией исполнителя", default=0)
	created = models.BooleanField(verbose_name="Создана", default=False)
	state = models.BooleanField(verbose_name="Статус", default=True)

	class Meta:
		verbose_name = "Заявки на задачу"
		verbose_name_plural = "Заявки на задачу"

	def __str__(self):
		return '{}|{}'.format(self.client, self.task.id)

@receiver(post_save, sender=Feedback)
def update_feedback(sender, **kwargs):
	from bot.classes.task import TaskClass
	instance = kwargs['instance']
	if(kwargs['update_fields']):
		if('created' in kwargs['update_fields']):
			feedback = instance
			task = TaskClass(feedback.task.client)
			task.preview_feedback(feedback.id)
			astudy.send_message(chat_id=task.client.chat_id, text=task.answer, reply_markup=task.keyboard, parse_mode="HTML")

class Review(CommonInfo):
	castomer = models.ForeignKey(Clients, on_delete=models.CASCADE,
								verbose_name="Заказчик", blank=True, null=True, related_name='customer_review')
	executor = models.ForeignKey(Clients, on_delete=models.CASCADE,
								verbose_name="Исполнитель", blank=True, null=True, related_name='executor_review')
	task = models.ForeignKey(Tasks, on_delete=models.CASCADE,
								verbose_name="Задача")
	message = models.TextField(verbose_name="Сообщение")

	class Meta:
		verbose_name = "Отзывы"
		verbose_name_plural = "Отзывы"

	def __str__(self):
		return '{}|{}'.format(self.castomer if self.executor is None else self.executor, self.task.id)

class Assessment(CommonInfo):
	castomer = models.ForeignKey(Clients, on_delete=models.CASCADE,
								verbose_name="Заказчик", blank=True, null=True, related_name='customer_asse')
	executor = models.ForeignKey(Clients, on_delete=models.CASCADE,
								verbose_name="Исполнитель", blank=True, null=True, related_name='executor_asse')
	task = models.ForeignKey(Tasks, on_delete=models.CASCADE,
								verbose_name="Задача")
	grade = models.IntegerField(verbose_name="Оценка")
	type_grade = models.CharField(verbose_name="Тип оценки", max_length=50, choices=TYPE_GRADE, blank=True, null=True)

	class Meta:
		verbose_name = "Оценки"
		verbose_name_plural = "Оценки"

	def __str__(self):
		return '{}|{}'.format(self.castomer if self.executor is None else self.executor, self.task.id)


class Preview_message(CommonInfo):
	customer = models.ForeignKey(Clients, on_delete=models.CASCADE,
								verbose_name="Заказчик", blank=True, null=True, related_name='customer_message')
	executor = models.ForeignKey(Clients, on_delete=models.CASCADE,
								verbose_name="Исполнитель", blank=True, null=True, related_name='executor_message')
	task = models.ForeignKey(Tasks, on_delete=models.CASCADE,
								verbose_name="Задача")
	message = models.TextField(verbose_name="Сообщение")
	state = models.BooleanField(verbose_name="Отправлено", default=False)

	class Meta:
		verbose_name = "Сообщения по заявке"
		verbose_name_plural = "Сообщения по заявке"

	def __str__(self):
		return '{}|{}'.format(self.customer if self.executor is None else self.executor, self.task.id)


class Cabinet(CommonInfo):
	client = models.ForeignKey(Clients, on_delete=models.CASCADE,
								verbose_name="Пользователь")
	role = models.CharField(verbose_name="Роль", max_length=50, choices=ROLE)
	task = models.ForeignKey(Tasks, on_delete=models.CASCADE,
								verbose_name="Задача")
	active = models.BooleanField(verbose_name="Пользователь в кабинете", default=False)
	state = models.BooleanField(verbose_name="Используется", default=True)
	grade = models.BooleanField(verbose_name="Оцениваеся", default=False)

	class Meta:
		verbose_name = "Кабинет"
		verbose_name_plural = "Кабинет"

	def __str__(self):
		return '{} {} {} {} {}'.format(self.client, self.role, self.task.id, self.active, self.state)

class Cabinetmessage(CommonInfo):
	cabinet_record = models.ForeignKey(Cabinet, on_delete=models.CASCADE,
								verbose_name="Пользователь")
	message = models.TextField(verbose_name="Сообщение", blank=True, null=True)
	file = models.ForeignKey(Files, verbose_name="Файл", blank=True, null=True, on_delete=models.CASCADE)
	state = models.BooleanField(verbose_name="Прочитано", default=False)

	class Meta:
		verbose_name = "Сообщения в кабинете"
		verbose_name_plural = "Сообщения в кабинете"

	def __str__(self):
		return '{} {}'.format(self.cabinet_record.id, self.message)

@receiver(post_save, sender=Cabinet)
def create_cabinet(sender, **kwargs):
	from bot.classes.task import TaskClass
	instance = kwargs['instance']
	created = kwargs['created']
	if(created):
		answer_1 = CABINET_START
		answer_2 = font('bold', 'Пожалуйста, активируйте заказ и ожидайте {} ⏳'.format('исполнителя' if instance.role == 'customer' else 'заказчика'))

		try:
			cabinet.send_message(chat_id=instance.client.chat_id, text=answer_1, parse_mode="HTML", disable_web_page_preview=True)
		except:
			pass
		try:
			cabinet.send_message(chat_id=instance.client.chat_id, text=answer_2, parse_mode="HTML")
		except:
			pass
	elif(kwargs['update_fields'] and 'active' in kwargs['update_fields']):
		role_interlocutor = 'customer' if instance.role == 'executor' else 'executor'
		cabinet_record = Cabinet.objects.filter(task=instance.task, role=role_interlocutor)
		if(instance.active):
			Cabinetmessage.objects.filter(cabinet_record__task=instance.task, cabinet_record__role=role_interlocutor).update(state=True)

			if(cabinet_record[0].active):
				answer_2 = font('bold', '{} зашёл в кабинет 👨'.format('Заказчик' if instance.role == 'customer' else 'Помощник'))
				cabinet.send_message(chat_id=cabinet_record[0].client.chat_id, text=answer_2, parse_mode="HTML")
				answer_1 = 'Вы активировали переписку\n{} уже тут ✅'.format('помощник' if instance.role == 'customer' else 'заказчик')
			else:
				answer_1 = 'Вы активировали переписку'

			from bot.classes.stairs import Stairs
			stairs = Stairs(None, None)
			keyboard = types.ReplyKeyboardMarkup(True)
			f = lambda A, n: [A[i:i+n] for i in range(0, len(A), n)]
			if(instance.role == 'customer'):
				keyboard.keyboard = f(stairs.buttons_cabinetcustomer, 2)
			else:
				keyboard.keyboard = f(stairs.buttons_cabinetexecutor, 2)
			cabinet.send_message(chat_id=instance.client.chat_id, text=answer_1, parse_mode="HTML", reply_markup=keyboard)

	elif(kwargs['update_fields'] and 'state' in kwargs['update_fields']):
		role_interlocutor = 'customer' if instance.role == 'executor' else 'executor'
		cabinet_record = Cabinet.objects.filter(task=instance.task, role=role_interlocutor, state=True)
		if(cabinet_record):
			answer = font('bold', '‼️ Помощник запрашивает окончание работ по заказу #{}\n'.format(instance.task.id))
			answer += font('light', '⚠️ Не принимайте окончание работ пока ее не проверил преподаватель. У вас есть гарантийный период 10 дней на протяжение которых, вы можете запросить у помощника корректировку работы')
			keyboard = types.InlineKeyboardMarkup(True)
			keyboard.keyboard.append([{'text': 'Принять ✅', 'callback_data': 'CABINET110_{}_{}'.format(cabinet_record[0].id, 'yes')}])
			keyboard.keyboard.append([{'text': 'Отклонить ❌', 'callback_data': 'CABINET110_{}_{}'.format(cabinet_record[0].id, 'no')}])
			cabinet.send_message(chat_id=cabinet_record[0].client.chat_id, text=answer, reply_markup=keyboard, parse_mode="HTML")
		else:
			task = Tasks.objects.filter(id=instance.task.id)[0]
			task.finish = True
			task.save(update_fields=['finish'])
			


class Deadlines(CommonInfo):
	name = models.CharField(verbose_name="Описание", max_length=100, blank=True, null=True)
	days = models.IntegerField(verbose_name="Дни", default=1)

	class Meta:
		verbose_name = "Сроки"
		verbose_name_plural = "Сроки"

	def __str__(self):
		return '{}'.format(self.name)

class Withdrawal(CommonInfo):
	client = models.ForeignKey(Clients, on_delete=models.CASCADE,
								verbose_name="Пользователь")
	amount_one = models.FloatField(verbose_name="Сумма без комиссии", default=0)
	amount_two = models.FloatField(verbose_name="Сумма с комиссией", default=0)
	state = models.BooleanField(verbose_name="Статус", default=False)

	class Meta:
		verbose_name = "Заявки на вывод"
		verbose_name_plural = "Заявки на вывод"

	def __str__(self):
		return '{}|{}'.format(self.client, 'Обработана' if self.state else 'Не обработана')


class Payliq(CommonInfo):
	client = models.ForeignKey(Clients, on_delete=models.CASCADE,
								verbose_name="Пользователь")
	amount_one = models.FloatField(verbose_name="Сумма без комиссии", default=0)
	amount_two = models.FloatField(verbose_name="Сумма с комиссией", default=0)
	token = models.CharField(verbose_name="Токен", max_length=200, blank=True, null=True)
	state = models.BooleanField(verbose_name="Статус", default=False)

	class Meta:
		verbose_name = "Пополнение баланса"
		verbose_name_plural = "Пополнение баланса"

	def __str__(self):
		return '{} {}'.format(self.client, self.token)

class Commissions(CommonInfo):
	amount_one = models.FloatField(verbose_name="Комиссия на пополнение", default=1)
	amount_two = models.FloatField(verbose_name="Комиссия на вывод", default=1)
	amount_three = models.FloatField(verbose_name="Комиссия заказчика", default=1)
	amount_four = models.FloatField(verbose_name="Комиссия исполнителя", default=1)

	class Meta:
		verbose_name = "Комиссия"
		verbose_name_plural = "Комиссия"

class DialogControll(CommonInfo):
	client = models.ForeignKey(Clients, on_delete=models.CASCADE,
									verbose_name="Пользователь")
	data = models.TextField(verbose_name="Доп параметры в jsons")
	bot = models.CharField(verbose_name="Бот", max_length=200, blank=True, null=True)

	class Meta:
		verbose_name = "Контроллер"
		verbose_name_plural = "Контроллеры"

	def __str__(self):
		return '{}'.format(self.client)