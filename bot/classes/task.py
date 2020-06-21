# -*- coding: utf-8 -*-
from datetime import datetime, date, timedelta
import calendar
import os
import math
from bot.models import *
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.core.files.base import ContentFile
from django.utils import timezone
from django.core.paginator import Paginator
from telebot import types
from io import BytesIO
from telebot.types import InputMediaPhoto, InputMediaVideo, InputMediaDocument
from django.db.models import Avg
from bot.classes.user import *
from astudy.settings import font, PAY_SUCCESS, constructor, search_list

class TaskClass:
	keyboard = ''
	answer = ''
	client = ''
	count_list = 9
	COUNT_ROW = 2
	lenght_preview = 20
	state = True
	task = ''
	docs = []

	def __init__(self, client, user='', id_task=None):
		self.client = client
		self.user = user
		self.commissions = Commissions.objects.filter()[0]
		if(id_task and self.user in ['CUSTOMERSEARCH', 'EXECUTORSEARCH', 'EXECUTOR', 'CABINET']):
			self.task = Tasks.objects.filter(id=int(id_task), created=True)[0]
		elif(self.user == 'CABINET'):
			self.cabinet = Cabinet.objects.filter(client=self.client, active=True)
			if(self.cabinet):
				self.cabinet = self.cabinet[0]
				self.task = self.cabinet.task
		else:
			self.task = Tasks.objects.filter(client=self.client, created=False)
			if(self.task): self.task = self.task[0]

	
	def font(self, type_font, message):
		font_array = {'bold': '<b>' + str(message) + '</b>', 'light': '<i>' + str(message) + '</i>'}
		return font_array[type_font]

	def calendar(self, month=None, year=None):
		self.answer = 'Выберите дату'
		month_list = {
						1: 'Январь',
						2: 'Февраль',
						3: 'Март',
						4: 'Апрель',
						5: 'Май',
						6: 'Июнь',
						7: 'Июль',
						8: 'Август',
						9: 'Сентябрь',
						10: 'Октябрь',
						11: 'Ноябрь',
						12: 'Декабрь',
					}
		if(month is None):
			month = datetime.now().month
		if(year is None):
			year = datetime.now().year

		self.keyboard = types.InlineKeyboardMarkup(True)
		calendar_deadline = calendar.Calendar(firstweekday=0)
		buttons = []
		for x in calendar_deadline.monthdatescalendar(year, month):
			for y in x:
				date_now = date(datetime.now().year, datetime.now().month, datetime.now().day)
				if(date_now > y or month != y.month):
					buttons.append({'text': '🔴', 'callback_data': '-'})
				else:
					buttons.append({'text': y.day, 'callback_data': 'CUSTOMER111_{}____'.format(y)})


		
		self.keyboard.keyboard.append([{'text': '{}-{}'.format(month_list[month],year), 'callback_data': '-'}])
		buttons_day = []
		buttons_day.append({'text': 'Пн', 'callback_data': '-'})
		buttons_day.append({'text': 'Вт', 'callback_data': '-'})
		buttons_day.append({'text': 'Ср', 'callback_data': '-'})
		buttons_day.append({'text': 'Чт', 'callback_data': '-'})
		buttons_day.append({'text': 'Пт', 'callback_data': '-'})
		buttons_day.append({'text': 'Сб', 'callback_data': '-'})
		buttons_day.append({'text': 'Вс', 'callback_data': '-'})

		self.keyboard.keyboard.append(buttons_day)

		for x in constructor(buttons, 7): self.keyboard.keyboard.append(x)

		buttons_paginator = []
		if(int(month) == 1):
			prev_year = int(year) - 1
			prev_month = 12
			next_year = int(year)
			next_month = int(month) + 1
		elif(int(month) == 12):
			prev_year = int(year)
			prev_month = int(month) - 1
			next_year = int(year) + 1
			next_month = 1
		else:
			prev_year = int(year)
			prev_month = int(month) - 1
			next_year = int(year)
			next_month = int(month) + 1

		date_prev = date(int(prev_year), int(prev_month), date_now.day)
		date_next = date(int(next_year), int(next_month), date_now.day)

		if(date_now <= date_prev):
			buttons_paginator.append({'text': '◀️', 'callback_data': 'CUSTOMER113_{}_{}_'.format(
					prev_month,
					prev_year)
			})
		buttons_paginator.append({'text': '▶️', 'callback_data': 'CUSTOMER113_{}_{}_'.format(
				next_month,
				next_year)
		})

		self.keyboard.keyboard.append(buttons_paginator)

	def create(self):
		self.task.created = True
		self.task.save(update_fields=['created'])
	
	def check_task(self):
		self.answer = 'Проверьте данные\n'
		self.answer += '✏️ Предмет: {}\n'.format(font('bold', self.task.subject.name))
		self.answer += '⏰ Срок сдачи до: {}\n'.format(font('bold', datetime.date(self.task.deadline)))
		self.answer += '📋 Описание заказа: {}\n'.format(font('bold', self.task.more))
		if(not self.task.files.all()): self.answer += '📪 Файлы не прикреплены\n'
		if(self.task.files.all()):
			self.answer += '📪 Ваши файлы:\n'
			for x in self.task.files.all():
				self.answer += '📎 {}\n'.format(str(x.upload).split('/')[-1])

		self.answer += font('light', '\nЕсли всё в порядке, нажмите {}, иначе нажмите {} и внесите изменения'.format(font('bold', '«Найти помощника 👌»'), font('bold', '«Назад ↩️»')))
		self.keyboard = types.InlineKeyboardMarkup(True)
		self.keyboard.keyboard.append([{'text': 'Найти помощника 👌', 'callback_data': 'CUSTOMER150____'}])
		# self.keyboard.keyboard.append([{'text': 'Отменить', 'callback_data': 'USER888'}])
		self.keyboard.keyboard.append([{'text': 'Назад ↩️', 'callback_data': 'CUSTOMER130____'}])

	def task_feedback(self, page=1):
		self.answer = 'Нажмите на цифру, чтобы открыть заявку\n'

		buttons = []
		i = int(page) * self.count_list - self.count_list
		data = Paginator(Feedback.objects.filter(task=self.task, state=True), self.count_list)
		data = data.page(int(page))
		for x in data.object_list:
			i += 1
			user = User(self.client.chat_id)
			user.raiting(x.task.subject.name, x.client)
			self.answer += '{}. 🎓 Помощник {} 💲{}\n{}\n'.format(i, font('bold', '№ {}'.format(x.client.id)), font('light', 'Цена: ') + font('bold', '{} грн'.format(math.ceil(x.price_two))), font('light', '💎 Рейтинг: {} ({})'.format(user.star, user.assessment)))
			buttons.append({'text': str(i), 'callback_data': 'CUSTOMER160_' + str(x.id) + '_inside___'})


		buttons_paginator = []
		if(data.has_previous()):
			buttons_paginator.append({'text': '◀️', 'callback_data': 'FEEDBACKPAGE_{}_{}'.format(
				data.previous_page_number(),
				self.task.id
				)
			})
		if(data.has_next()):
			buttons_paginator.append({'text': '▶️', 'callback_data': 'FEEDBACKPAGE_{}_{}'.format(
				data.next_page_number(),
				self.task.id
				)
			})


		if(not buttons): 
			self.answer = 'Помощники еще оценивают ваш заказ ⚖️\n'
			self.answer += font('light', 'Ожидайте уведомлениями с новыми оценками ⏱')
		self.keyboard = types.InlineKeyboardMarkup(True)
		self.keyboard.keyboard = constructor(buttons, self.COUNT_ROW)
		self.keyboard.keyboard.append(buttons_paginator)
		self.keyboard.keyboard.append([{'text': 'Назад ↩️', 'callback_data': 'CUSTOMERSEARCH110_' + str(self.task.id)}])

	def preview_feedback(self, id_feedback):
		feedback = Feedback.objects.filter(id=id_feedback)[0]
		user = User(self.client.chat_id)
		user.raiting(feedback.task.subject.name, feedback.client)
		self.answer += '🎓 Помощник {} готов взяться за ваше задание #{}!\n{}\n💲{}'.format(
			font('bold', '№ {}'.format(feedback.client.id)),
			font('bold', feedback.task.id),
		 	font('light', '\n💎 Рейтинг: {} ({})'.format(user.star, font('bold', user.assessment))), 
		 	font('light', 'Цена: ') + font('bold', '{} грн'.format(math.ceil(feedback.price_two))),
		)
		self.keyboard = types.InlineKeyboardMarkup(True)
		self.keyboard.keyboard.append([{'text': 'Подробнее', 'callback_data': 'CUSTOMER160_' + str(feedback.id) + '_____'}])

	def show_feedback(self, id_feedback):
		feedback = Feedback.objects.filter(id=id_feedback)[0]
		self.task = feedback.task
		executor = feedback.client

		user = User(self.client.chat_id)
		user.raiting(feedback.task.subject.name, executor)
		task_countone = Tasks.objects.filter(executor=executor, finish=True).count()
		task_counttwo = Tasks.objects.filter(subject=feedback.task.subject, executor=executor, finish=True).count()
		self.answer += '🎓 Помощник: {}\n💲 Цена: {}\n✉️ Комментарий: {}\n'.format(font('bold', '№ {}'.format(feedback.client.id)), font('bold', '{} грн'.format(math.ceil(feedback.price_two))), font('bold',feedback.question))
		self.answer += '💎 Рейтинг: {} ({})\n'.format(user.star, font('bold', user.assessment))
		self.answer += '🏆 Выполнено работ: {}\n'.format(font('bold', task_countone))
		self.answer += '🏆 {}: {}\n'.format(self.task.subject.name, font('bold', task_counttwo))
		self.keyboard = types.InlineKeyboardMarkup(True)
		buttons = []
		buttons.append({'text': 'Выбрать 🥇', 'callback_data': 'CUSTOMER170_' + str(feedback.id) + '____'})
		buttons.append({'text': 'Ответить 💬', 'callback_data': 'CUSTOMER200_' + str(id_feedback) + '_customer___'})
		buttons.append({'text': 'Отказаться ❌', 'callback_data': 'CUSTOMER171_' + str(feedback.id) + '____'})
		
		self.keyboard = types.InlineKeyboardMarkup(True)
		self.keyboard.keyboard = constructor(buttons, self.COUNT_ROW)

	def payment_feedback(self, id_feedback):
		feedback = Feedback.objects.filter(id=id_feedback)[0]
		if(self.client.bonuse): price = feedback.price_two
		else: price = feedback.price_two / self.commissions.amount_four

		self.client.bonuse = False
		self.client.save(update_fields=['bonuse'])
		if(self.client.bonuse):
			self.answer = '💲 Цена с учетом комиссии сервиса: {} (Без скидки {})'.format(font('bold', str(math.ceil(price)) + ' грн'), font('bold', str(math.ceil(feedback.price_two / self.commissions.amount_four)  + ' грн')))
		else:
			self.answer = '💲 Цена с учетом комиссии сервиса: {}'.format(font('bold', str(math.ceil(price)) + ' грн'))
		self.keyboard = types.InlineKeyboardMarkup(True)
		self.keyboard.keyboard.append([{'text': 'Оплатить ✔️', 'callback_data': 'CUSTOMER180_' + str(feedback.id) + '____'}])

	def accept_feedback(self, id_feedback):
		feedback = Feedback.objects.filter(id=id_feedback)[0]
		if(self.client.bonuse): price = feedback.price_two
		else: price = feedback.price_two / self.commissions.amount_four
		if(self.client.balance >= math.ceil(price)):
			feedback.state = True
			feedback.save(update_fields=['state'])
			self.task = Tasks.objects.filter(id=feedback.task.id)[0]
			if(self.task.executor):
				self.state = False
				return
			self.task.executor = feedback.client
			self.task.price_one = feedback.price_two
			self.task.price_two = math.ceil(price)
			self.task.state = True
			self.task.save(update_fields=['executor', 'price_one', 'price_two', 'state'])
			self.client.balance -= math.ceil(price)
			self.client.save(update_fields=['balance'])
			self.answer = PAY_SUCCESS.format(font('bold', '#{} {}'.format(feedback.task.id, feedback.task.subject.name)))
		else:
			self.answer = 'У вас недостаточно средств ☹️'

	def refuse_feedback(self, id_feedback):
		self.feedback = Feedback.objects.filter(id=id_feedback)[0]
		if(self.feedback.state):
			self.feedback.state = False
			self.feedback.save(update_fields=['state'])
			self.answer = 'Заказчик отклонил вашу заявку на заказ {}☹️'.format(font('bold', '#{} {}'.format(self.feedback.task.id, self.feedback.task.subject.name)))
		else:
			self.state = False
			self.answer = 'Действие уже выполнено'

	def create_message(self, id_feedback, reciver, message):
		feedback = Feedback.objects.filter(id=id_feedback)[0]
		self.keyboard = types.InlineKeyboardMarkup(True)
		self.answer = 'Заказ {}\n'.format(font('bold', '#{} {}'.format(feedback.task.id, feedback.task.subject.name)))
		if(reciver == 'executor'):
			feedback_message = Preview_message.objects.filter(task=feedback.task, customer=feedback.task.client, state=False)
			if(feedback_message):
				feedback_message = feedback_message[0]
				feedback_message.message = message
				feedback_message.save(update_fields=['message'])
			else:
				feedback_message = Preview_message.objects.create(task=feedback.task, customer=feedback.task.client, message=message)

			feedback_customer = Preview_message.objects.filter(task=feedback.task, executor=feedback.client, state=True).order_by('-id')
			if(feedback_customer):
				feedback_customer = feedback_customer[0]
				self.answer += 'Сообщение от помощника №{}: {}\n'.format(feedback.client.id, font('bold', feedback_customer.message))
			self.answer += 'Ваше сообщение: {}'.format(font('bold', message))
		elif(reciver == 'customer'):
			feedback_message = Preview_message.objects.filter(task=feedback.task, executor=feedback.client, state=False)
			if(feedback_message):
				feedback_message = feedback_message[0]
				feedback_message.message = message
				feedback_message.save(update_fields=['message'])
			else:
				feedback_message = Preview_message.objects.create(task=feedback.task, executor=feedback.client, message=message)

			feedback_executor = Preview_message.objects.filter(task=feedback.task, customer=feedback.task.client, state=True).order_by('-id')
			if(feedback_executor):
				feedback_executor = feedback_executor[0]
				self.answer += 'Сообщение от заказчика: {}\n'.format(font('bold', feedback_executor.message))
			self.answer += 'Ваше сообщение: {}'.format(font('bold', message))

		
		self.keyboard.keyboard.append([{'text': 'Отправить 📨', 'callback_data': 'CUSTOMER210_' + str(id_feedback) + '_' + reciver + '___'}])
		if(reciver == 'executor'): self.keyboard.keyboard.append([{'text': 'Отменить ❌', 'callback_data': 'CUSTOMER888_' + str(id_feedback) + '_customer___'}])
		elif(reciver == 'customer'): self.keyboard.keyboard.append([{'text': 'Отменить ❌', 'callback_data': 'CUSTOMER888_' + str(id_feedback) + '_executor___'}])

	def send_message(self, id_feedback, reciver, type_call='outside'):
		feedback = Feedback.objects.filter(id=id_feedback)[0]
		self.keyboard = types.InlineKeyboardMarkup(True)
		self.answer = '✉️ Заказ {}\n'.format(font('bold', '#{} {}'.format(feedback.task.id, feedback.task.subject.name)))
		if(reciver == 'executor'):
			if(type_call == 'outside'):
				feedback_message = Preview_message.objects.filter(task=feedback.task.id, customer=feedback.task.client, state=False)[0]
				feedback_message.state = True
			elif(type_call == 'inside'):
				feedback_message = Preview_message.objects.filter(task=feedback.task.id, customer=feedback.task.client, state=True).order_by('-id')[0]
			self.answer += 'Сообщение от заказчика: {}\n'.format(font('bold', feedback_message.message))
			self.chat_id = feedback.client.chat_id
		elif(reciver == 'customer'):
			if(type_call == 'outside'):
				feedback_message = Preview_message.objects.filter(task=feedback.task.id, executor=feedback.client, state=False)[0]
				feedback_message.state = True
			elif(type_call == 'inside'):
				feedback_message = Preview_message.objects.filter(task=feedback.task.id, executor=feedback.client, state=True).order_by('-id')
				if not feedback_message:
					self.answer = 'Действие отменено'
					return
				else:
					feedback_message = feedback_message[0]
			self.answer += 'Сообщение от помощника №{}: {}\n'.format(feedback.client.id, font('bold', feedback_message.message))
			self.chat_id = feedback.task.client.chat_id
			self.keyboard.keyboard.append([{'text': 'Показать заявку', 'callback_data': 'CUSTOMER160_' + str(feedback.id) + '_____'}])

		feedback_message.save(update_fields=['state'])
		self.keyboard.keyboard.append([{'text': 'Ответить 💬', 'callback_data': 'CUSTOMER200_' + str(id_feedback) + '_' + reciver + '___'}])

	def show_task(self, search=False):
		if(self.user == 'EXECUTOR'):
			if(not self.task.executor):
				self.answer += '✏️ Предмет: {}\n'.format(font('bold', self.task.subject.name + ' #' + font('bold', str(self.task.id))))
				self.answer += '⏰ Срок сдачи до: {}\n'.format(font('bold', datetime.date(self.task.deadline)))
				self.answer += '📋 Описание заказа: {}\n'.format(font('bold', self.task.more))
				if(not self.task.files.all()): self.answer += '📪 Файлы не прикреплены\n'

				self.keyboard = types.InlineKeyboardMarkup(True)
				if(not Feedback.objects.filter(client=self.client, task=self.task, created=True)):
					self.keyboard.keyboard.append([{'text': 'Оценить', 'callback_data': 'EXECUTOR120_' + str(self.task.id) + search_list[search]['postfix']}])
				if(self.task.files.all()): self.keyboard.keyboard.append([{'text': 'Файлы 🖇', 'callback_data':  'EXECUTOR101_' + str(self.task.id)}])
				if(search):
					self.keyboard.keyboard.append([{'text': 'Назад ↩️', 'callback_data': 'EXECUTOR888__'}])
				else:
					self.keyboard.keyboard.append([{'text': 'Скрыть', 'callback_data': 'EXECUTOR999_' + str(self.task.id)}])
			else:
				self.answer += 'Исполнитель уже выбран'
		elif(self.user == 'CUSTOMERSEARCH'):
			self.answer += '✏️ Предмет: {}\n'.format(font('bold', self.task.subject.name + ' #' + font('bold', str(self.task.id))))
			self.answer += '⏰ Срок сдачи до: {}\n'.format(font('bold', datetime.date(self.task.deadline)))
			self.answer += '📋 Описание заказа: {}\n'.format(font('bold', self.task.more))
			# self.answer += 'Исполнитель: {}\n'.format('Не выбран' if not self.task.executor else self.task.executor.id)
			if(not self.task.files.all()): self.answer += '📪 Файлы не прикреплены\n'
			self.answer += '💲 Цена: {}\n'.format(font('bold', 'Помощник не выбран') if not self.task.price_two else font('bold', str(math.ceil(self.task.price_two)) + ' грн'))
			if(self.task.files.all()):
				self.answer += '📪 Ваши файлы:\n'
				for x in self.task.files.all():
					self.answer += '📎 {}\n'.format(str(x.upload).split('/')[-1])

			self.keyboard = types.InlineKeyboardMarkup(True)
			buttons = []

			if(not self.task.executor): 
				buttons.append({'text': 'Файлы ✍️', 'callback_data': 'CUSTOMERSEARCH130_' + str(self.task.id)})
				buttons.append({'text': 'Описание ✍️', 'callback_data': 'CUSTOMERSEARCH120_' + str(self.task.id)})
			if(self.task.files.all()): buttons.append({'text': 'Файлы 🖇', 'callback_data': 'EXECUTOR101_' + str(self.task.id)})
			if(not self.task.executor): buttons.append({'text': 'Удалить ❌', 'callback_data': 'CUSTOMERSEARCH160_' + str(self.task.id)})

			self.keyboard.keyboard = constructor(buttons, self.COUNT_ROW)
			if(self.task.executor and not self.task.state): 
				self.keyboard.keyboard.append([{'text': 'Кабинет', 'url': '#'}])
			if(not self.task.executor): 
				self.keyboard.keyboard.append([{'text': 'Заявки помощников 💎', 'callback_data': 'CUSTOMERSEARCH150_' + str(self.task.id)}])
			self.keyboard.keyboard.append([{'text': 'Назад ↩️', 'callback_data': 'CUSTOMERSEARCH170____'}])
		elif(self.user == 'EXECUTORSEARCH'):
			self.answer += '✏️ Предмет: {}\n'.format(self.task.subject.name + ' #' + font('bold', str(self.task.id)))
			self.answer += '⏰ Срок сдачи до: {}\n'.format(font('bold', datetime.date(self.task.deadline)))
			self.answer += '📋 Описание заказа: {}\n'.format(font('bold', self.task.more))
			if(not self.task.files.all()): self.answer += '📪 Файлы не прикреплены\n'
			self.answer += '💲 Цена: {} грн\n'.format(font('bold', math.ceil(self.task.price_one)))

			self.keyboard = types.InlineKeyboardMarkup(True)
			self.keyboard.keyboard.append([{'text': 'Кабинет', 'url': '#'}])

		elif(self.user == 'CABINET'):
			self.answer += '✏️ Предмет: {}\n'.format(font('bold', self.task.subject.name + ' #' + str(self.task.id)))
			self.answer += '⏰ Срок сдачи до: {}\n'.format(font('bold', datetime.date(self.task.deadline)))
			self.answer += '📋 Описание заказа: {}\n'.format(font('bold', self.task.more))
			if(not self.task.files.all()): self.answer += '📪 Файлы не прикреплены\n'
			self.answer += '💲 Цена: {} грн\n'.format(font('bold', math.ceil(self.task.price_one)))

			self.keyboard = types.InlineKeyboardMarkup(True)
			self.keyboard.keyboard.append([{'text': 'Показать файлы 🖇', 'callback_data': 'EXECUTOR101_' + str(self.task.id)}])

	def select_task(self, page=1):
		self.keyboard = types.InlineKeyboardMarkup(True)
		buttons = []
		data_res = []
		prefix = ''
		if(self.user == 'EXECUTOR'):
			data_prev = Tasks.objects.filter(executor=None, created=True, finish=False).order_by('-id')
			for x in data_prev:
				if(Clients.objects.filter(filter_subjects=x.subject, id=self.client.id) and x.client.id != self.client.id):
					data_res.append(x)
			data = Paginator(data_res, self.count_list)
			post_data = self.user + '110_{}'
			page_data = self.user + 'PAGE_'

		elif(self.user == 'CUSTOMERSEARCH'):
			data = Paginator(Tasks.objects.filter(client=self.client, created=True, finish=False).order_by('-id'), self.count_list)
			post_data = self.user + '110_{}'
			page_data = self.user + 'PAGE_'

		elif(self.user == 'EXECUTORSEARCH'):
			data = Paginator(Tasks.objects.filter(executor=self.client, finish=False), self.count_list)
			post_data = 'EXECUTOR150_{}_inside___'
			page_data = self.user + 'PAGE_'

		data = data.page(int(page))
		i = int(page) * self.count_list - self.count_list
		for x in data.object_list:
			i += 1
			prefix = ''
			if(self.user == 'EXECUTOR'):
				feedback = Feedback.objects.filter(client=self.client, task=x, created=True)
				if(feedback):
					feedback = feedback[0]
					prefix = '✅ {} грн'.format(feedback.price_one)
			self.answer += '{}. {} {} {} ({})\n'.format(i, prefix, x.subject.name, font('bold', '#{}'.format(x.id)), (x.more[:self.lenght_preview] + '...') if len(x.more) > self.lenght_preview else x.more)
			buttons.append({'text': str(i), 'callback_data': post_data.format(x.id)})

		buttons_paginator = []
		if(data.has_previous()):
			buttons_paginator.append({'text': '◀️', 'callback_data': page_data + '{}'.format(
				data.previous_page_number())
			})
		if(data.has_next()):
			buttons_paginator.append({'text': '▶️', 'callback_data': page_data + '{}'.format(
				data.next_page_number())
			})


		if(buttons):
			self.answer = 'Нажимайте на кнопки ниже для перехода на задачи\n' + self.answer
			self.keyboard.keyboard = constructor(buttons, 3)
			self.keyboard.keyboard.append(buttons_paginator)
		else:
			self.answer = 'Задачи не найдены'

	def update_task(self, action, message=None, subject=None, file_name=None):
		if(action == 'create'):
			if(subject):
				search = Tasks.objects.filter(client=self.client, created=False)
				if(search): search.delete()
				self.task = Tasks.objects.create(client=self.client, subject=subject)

			self.answer = '✏️ Предмет: {}\n'.format(font('bold',self.task.subject.name))
			self.answer += font('light','⏰ Укажите {} сдачи до'.format(font('bold', 'срок')))
			self.keyboard = types.InlineKeyboardMarkup(True)
			buttons = []
			for x in Deadlines.objects.all():
				date_now = datetime.date(datetime.now() + timedelta(days=x.days))
				buttons.append({'text': x.name, 'callback_data': 'CUSTOMER111_{}____'.format(date_now)})

			self.keyboard.keyboard = constructor(buttons, self.COUNT_ROW)
			self.keyboard.keyboard.append([{'text': 'Календарь', 'callback_data': 'CUSTOMER112____'}])

		elif(action == 'description'):
			self.task.more = message
			self.task.save(update_fields=['more'])
			self.answer = message
			self.keyboard = types.InlineKeyboardMarkup(True)
			buttons = []
			buttons.append({'text': 'Назад ↩️', 'callback_data': 'CUSTOMER112____'})
			buttons.append({'text': 'Далее ➡️', 'callback_data': 'CUSTOMER130____'})
			buttons.append({'text': 'Отменить ❌', 'callback_data': 'CUSTOMER112____'})

			self.keyboard.keyboard = constructor(buttons, self.COUNT_ROW)

		elif(action == 'files'):
			with open("#" + file_name, "wb") as f:
				f.write(message)
			reopen = open("#" + file_name, "rb")
			django_file = File(reopen)
			self.task.files.add(Files.objects.create(upload=django_file))
			self.task.save()
			os.remove("#" + file_name)

			self.keyboard = types.InlineKeyboardMarkup(True)
			buttons = []
			if(self.user == 'CUSTOMERSEARCH'):
				buttons.append({'text': 'Применить', 'callback_data': 'CUSTOMERSEARCH140_' + str(self.task.id)})
			elif(self.user == 'CUSTOMERCREATE'):
				buttons.append({'text': 'Назад ↩️', 'callback_data': 'CUSTOMER120____'})
				buttons.append({'text': 'Далее ➡️', 'callback_data': 'CUSTOMER140____'})
				buttons.append({'text': 'Отменить ❌', 'callback_data': 'CUSTOMER120____'})

			self.keyboard.keyboard = constructor(buttons, self.COUNT_ROW)
			self.answer = '📪 Ваши файлы\n'
			for x in self.task.files.all():
				self.answer += '📎 {}\n'.format(str(x.upload).split('/')[-1])

		elif(action == 'deadline'):
			self.task.deadline = datetime.strptime(message + ' 0:0:0', '%Y-%m-%d %H:%M:%S')
			self.task.save(update_fields=['deadline'])
			self.answer = message
			self.keyboard = types.InlineKeyboardMarkup(True)
			buttons = []
			buttons.append({'text': 'Назад ↩️', 'callback_data': 'CUSTOMER112____'})
			buttons.append({'text': 'Далее ➡️', 'callback_data': 'CUSTOMER120____'})
			buttons.append({'text': 'Отменить ❌', 'callback_data': 'CUSTOMER112____'})

			self.keyboard.keyboard = constructor(buttons, self.COUNT_ROW)

	def delete_task(self):
		self.task.delete()
	
	def update_feedback(self, action, message=None, search=False):
		if(action == 'create+price'):
			price_two = math.ceil(float(message) / self.commissions.amount_three)
			Feedback.objects.filter(client=self.client, task=self.task).delete()
			Feedback.objects.create(client=self.client, task=self.task, price_one=message, price_two=price_two)

		elif(action == 'question'):
			feedback = Feedback.objects.filter(client=self.client, task=self.task, created=False)[0]
			feedback.question = message
			feedback.save(update_fields=['question'])
			self.answer = '{}:\nЦена, с учётом комиссии: {}\nКомментарий: {}'.format(font('bold', 'Проверьте данные'), font('bold', str(math.ceil(feedback.price_two)) + ' грн'), font('bold', feedback.question))
			self.keyboard = types.InlineKeyboardMarkup(True)
			buttons = []
			buttons.append({'text': 'Отправить 📨', 'callback_data': 'EXECUTOR140_' + str(self.task.id)})
			buttons.append({'text': 'Назад ↩️', 'callback_data': 'EXECUTOR130_' + str(self.task.id) + search_list[search]['postfix']})
			self.keyboard.keyboard = constructor(buttons, self.COUNT_ROW)
			self.keyboard.keyboard.append([{'text': 'Отменить ❌', 'callback_data': search_list[search]['callback_data'] + str(self.task.id)}])

		elif(action == 'active'):
			feedback = Feedback.objects.filter(client=self.client, task=self.task, created=False)
			if(feedback):
				feedback = feedback[0]
				feedback.created = True
				feedback.save(update_fields=['created'])
				self.answer = 'Заявка отправлена'
			else:
				self.answer = 'Заявка уже отправлена'

		elif(action == 'cancel'):
			feedback = Feedback.objects.filter(client=self.client, task=self.task)[0]
			if(not feedback.state):
				self.state = False
				return

			feedback.state = False
			feedback.save(update_fields=['state'])
			customer = Clients.objects.filter(id=self.task.client.id)[0]
			self.task.executor = None
			self.task.state = False
			self.task.save(update_fields=['executor', 'state'])
			customer.balance += self.task.price_two
			customer.save(update_fields=['balance'])
			self.answer = 'Вы отказались от заказа {} ☹️'.format(font('bold', '#{}-{}'.format(feedback.task.id, feedback.task.subject.name)))
			self.answer_customer = 'Помощник {} отказался от задачи {}\nЕго заявка больше не будет показываться ☹️\n'.format(font('bold', '# ' + str(feedback.client.id)), font('bold', '#{}-{}'.format(feedback.task.id, feedback.task.subject.name)))
			self.answer_customer += 'Выберите другого помощника 🤓'
			self.chat_id = customer.chat_id


		elif(action == 'accept'):
			if(not Cabinet.objects.filter(task=self.task)):
				feedback = Feedback.objects.filter(client=self.client, task=self.task)[0]
				self.answer = '🔥 Вы подтвердили начало работы над заказом {}\n'.format(font('bold', '#{}-{}'.format(feedback.task.id, feedback.task.subject.name)))
				self.answer += font('light', 'Работа должна быть выполнена не позднее срока сдачи, указанного заказчиком.\n')
				self.answer += font('light', 'Пожалуйста, переходите в ')
				self.answer += font('bold', '«Кабинет» ')
				self.answer += font('light', 'и приступайте к выполнению работы')
				self.answer_customer = 'Помощник {} подтвердил начало работы по заказу {}\n'.format(font('bold','№ {}'.format(feedback.client.id)), font('bold','# {} {}'.format(feedback.task.id, feedback.task.subject.name)))
				self.answer_customer += '{} {} {}'.format(font('light','Переходите в'), font('bold','«Кабинет»'), font('light','для уточнения деталей с помощником 🤝'))
				self.chat_id = feedback.task.client.chat_id
				self.task.state = False
				self.task.save(update_fields=['state'])
				self.keyboard_executor = types.InlineKeyboardMarkup(True)
				self.keyboard_executor.keyboard.append([{'text': 'Подробнее', 'callback_data': 'EXECUTOR150_' + str(feedback.task.id) + '_outside'}])
				self.keyboard_customer = types.InlineKeyboardMarkup(True)
				self.keyboard_customer.keyboard.append([{'text': 'Подробнее', 'callback_data': 'CUSTOMERSEARCH110_' + str(feedback.task.id)}])
				Cabinet.objects.create(client=self.client, task=self.task, role='executor')
				Cabinet.objects.create(client=feedback.task.client, task=self.task, role='customer')
			else:
				self.state = False

	def task_list(self):
		cabinets = Cabinet.objects.filter(client=self.client, task__finish=False).order_by('id') | Cabinet.objects.filter(client=self.client, grade=True).order_by('id')
		
		buttons = []
		self.answer = 'Выберите номер заказа, который хотите активировать\nЗ-заказчик, П-помощник'
		for x in cabinets:
			role_interlocutor = 'П' if x.role == 'executor' else 'З'
			postfix = '✅' if x.active else ''

			role_data = 'customer' if x.role == 'executor' else 'executor'
			cabinet_interlocutor = Cabinet.objects.filter(task=x.task, role=role_data)[0]
			unread = Cabinetmessage.objects.filter(cabinet_record=cabinet_interlocutor, state=False).count()
			buttons.append({'text': '{} #{}-{} ({})'.format(postfix, x.task.id, role_interlocutor, unread), 'callback_data': 'CABINET100_' + str(x.id)})

		self.keyboard = types.InlineKeyboardMarkup(True)
		self.keyboard.keyboard = constructor(buttons, self.COUNT_ROW)

	def task_active(self, id_cabinet):
		cabinet = Cabinet.objects.filter(id=id_cabinet)[0]
		self.state = False
		if(not cabinet.active):
			self.state = True
			unactive = Cabinet.objects.filter(client=self.client, active=True)
			if(unactive):
				unactive = unactive[0]
				unactive.active = False
				unactive.save(update_fields=['active'])
				role_interlocutor = 'customer' if unactive.role == 'executor' else 'executor'
				cabinet_interlocutor = Cabinet.objects.filter(task=unactive.task, role=role_interlocutor, active=True)
				self.answer = ''
				if(cabinet_interlocutor):
					self.answer = font('bold', '{} оффлайн ⏳'.format('Помощник' if cabinet_interlocutor[0].role == 'customer' else 'Заказчик'))
					self.chat_id = cabinet_interlocutor[0].client.chat_id

			cabinet.active = True
			cabinet.save(update_fields=['active'])

	def message_list(self):
		messages = Cabinetmessage.objects.filter(cabinet_record__task=self.task)
		if(messages):
			for x in messages:
				if(x.message):
					self.answer += '{}: {}\n'.format('Вы' if x.cabinet_record.role == self.cabinet.role else ('Заказчик' if x.cabinet_record.role == 'customer' else 'Исполнитель'), x.message)
				elif(x.file):
					self.answer += '{}: <a href="{}">Ссылка на файл</a>\n'.format('Вы' if x.cabinet_record.role == self.cabinet.role else ('Заказчик' if x.cabinet_record.role == 'customer' else 'Исполнитель'), '#' + str(x.file).split('/')[-1])
		else:
			self.answer += 'Сообщений не найдено'

	def message_cabinet(self, message):
		cabinet = Cabinet.objects.filter(client=self.client, active=True)[0]
		role_interlocutor = 'customer' if cabinet.role == 'executor' else 'executor'
		name_interlocutor = 'помощника' if cabinet.role == 'executor' else 'заказчика'
		cabinet_interlocutor = Cabinet.objects.filter(task=cabinet.task, role=role_interlocutor)[0]
		if(cabinet_interlocutor.active):
			Cabinetmessage.objects.create(cabinet_record=cabinet, message=message, state=True)
			self.answer += font('light', 'Сообщение от {}:\n'.format(name_interlocutor)) + message
			self.chat_id = cabinet_interlocutor.client.chat_id
		else:
			from astudy.settings import ASTUDY_TOKEN
			astudy = telebot.TeleBot(ASTUDY_TOKEN)
			answer = '🔔 У Вас новое сообщение по заказу {}\n'.format(font('bold', '#{} {}'.format(cabinet.task.id, cabinet.task.subject.name)))
			answer += font('light', 'Перейдите в ') + font('bold', '«Кабинет» ') + font('light', 'и прочитайте его')
			keyboard = types.InlineKeyboardMarkup(True)
			keyboard.keyboard.append([{'text': 'Кабинет', 'url': '#'}])
			astudy.send_message(chat_id=cabinet_interlocutor.client.chat_id, text=answer, parse_mode='HTML', reply_markup=keyboard)
			Cabinetmessage.objects.create(cabinet_record=cabinet, message=message)

	def exit_cabinet(self, position):
		if(position == 'yes' and Cabinet.objects.filter(client=self.client, task=self.task, state=True)):
			cabinet = Cabinet.objects.filter(client=self.client, task__finish=False, task=self.task)[0]
			cabinet.state = False
			cabinet.grade = True
			cabinet.save(update_fields=['state', 'grade'])
		elif(position == 'no'):
			Cabinet.objects.filter(task__finish=False, task=self.task).update(state=True)
			self.answer = 'Заказчик отклонил окончание работ ☹️'
			cabinet_interlocutor = Cabinet.objects.filter(task=self.task, role='executor')[0]
			self.chat_id = cabinet_interlocutor.client.chat_id
		else:
			self.state = False

	def get_type_grade(self, cabinet_id, type_grade, role):
		self.keyboard = types.InlineKeyboardMarkup(True)
		star = '⭐️'
		grade = {'two': '2', 'three': '3', 'four': '4'}
		grade_text = {'two': font('bold', 'скорость ответа'), 'three': font('bold', 'оформление'), 'four': font('bold', 'вежливость')}
		for x in range(5):
			self.keyboard.keyboard.append([{'text': star, 'callback_data': 'CABINET12{}_'.format(grade[type_grade]) + cabinet_id + '_' + role + '_' + str(x)}])
			star += '⭐️'

		self.answer = 'Оцените {}'.format(grade_text[type_grade])
	
	def task_grade(self, type_grade, ball, role):
		# role_interlocutor = 'customer' if role == 'executor' else 'executor'
		# cabinet_interlocutor = Cabinet.objects.filter(task=self.task, role=role_interlocutor)[0]
		# if(role == 'customer' and not Assessment.objects.filter(task=self.task, castomer=self.client, grade=int(ball), type_grade=type_grade)): 
		# 	Assessment.objects.create(task=self.task, castomer=self.client, grade=int(ball), type_grade=type_grade)
		if(role == 'executor' and not Assessment.objects.filter(task=self.task, executor=self.task.executor, grade=int(ball), type_grade=type_grade)): 
			Assessment.objects.create(task=self.task, executor=self.task.executor, grade=int(ball), type_grade=type_grade)
		else:
			self.state = False

	def task_review(self, message, role):
		if(role == 'customer'): Review.objects.create(task=self.task, castomer=self.client, message=message)
		elif(role == 'executor'): Review.objects.create(task=self.task, executor=self.client, message=message)

	def task_finish(self, role):
		Cabinet.objects.filter(task=self.task, client=self.client).update(active=False, grade=False)