# -*- coding: utf-8 -*-
import datetime
from bot.models import *
from bot.classes.subject import SubjectClass
from bot.classes.task import TaskClass
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from telebot import types
from telebot.types import InputMediaPhoto, InputMediaVideo
from datetime import datetime, date, timedelta
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.core.files.base import ContentFile
import os
import math
from astudy.settings import font, constructor, search_list, REFERAL_TEXT, SUPPORT_TEXT, INFO_TEXT

class Stairs:

	def __init__(self, user, bot):
		self.COUNT_ROW = 2
		self.user = user
		if(user is None):
			self.client = None
			self.dialog = None
		else:
			self.client = self.user.client
			self.dialog = self.user.dialog
		self.telegram_bot = bot
		self.delete_dialog = False
		self.data_dialog = ''
		self.answer = ''

		self.buttons_start = ['Новый заказ ➕',
								'Мой баланс 💰',
								'Мои заказы 📝',
								'Помощь 💻',
								'Меню помощника 🎓'
								]

		# self.buttons_customer = ['Новый заказ ➕',
		# 						'Мои заказы 📝',
		# 						'Назад ↩️',
		# 						]

		self.buttons_executor = ['Найти заказ 🔍',
								'Мои заказы 👨',
								'Категории 🗂',
								'Профиль 📖',
								'Назад ↩️',
								]

		self.buttons_cabinetcustomer = ['Показать заказ 🔖',
								'История 💬',
								'Навигация 🕸',
								]

		self.buttons_cabinetexecutor = ['Показать заказ 🔖',
								'История 💬',
								'Навигация 🕸',
								'Завершить заказ ☑️',
								]

		self.keyboard_cancel = types.InlineKeyboardMarkup(True)
		self.keyboard_cancel.keyboard = constructor([{'text': 'Отменить ❌', 'callback_data': 'USER888'}], 1)

	def isint(self, s):
		try:
			int(s)
			return True
		except ValueError:
			return False

	def isfloat(self, s):
		try:
			float(s)
			return True
		except ValueError:
			return False

	def between(self, message, a, b):
		if not (a <= float(message) <= b):
			self.answer = 'Введите число от {} до {}'.format(a, b)
			return False
		return True

	def len_string(self, message, a):
		if (len(message) > a):
			self.answer = 'Ограничение {} символов'.format(a)
			return False
		return True

	def font(self, type_font, message):
		font_array = {'bold': '<b>' + str(message) + '</b>', 'light': '<i>' + str(message) + '</i>'}
		return font_array[type_font]

	def quick_response(self, message, data=None):
		if(self.telegram_bot.get_me().username == 'Shpargalochka_bot'):
			if(message == '/start'):
				self.answer = 'Главное меню'
				keyboard = types.ReplyKeyboardMarkup(True)
				keyboard.keyboard = constructor(self.buttons_start, self.COUNT_ROW)
				self.telegram_bot.send_message(chat_id=self.client.chat_id, text=self.answer, parse_mode='HTML', reply_markup=keyboard)
			elif(message == 'профиль 📖'):
				self.user.card_raiting()
				self.answer = '{}\nИмя: {}\nСтрана: {}\nПодробнее обо мне: {}\nКуда выводить ср-ва: {}\n💎Рейтинг: {} ({})\n🏆Выполнено работ: {}\n'.format(
								font('bold', '🔥Ваша карточка 🔥'),
								font('bold', 'Не указано' if not self.client.name else self.client.name),
								font('bold', 'Не указано' if not self.client.city else self.client.city),
								font('bold', 'Не указано' if not self.client.more else self.client.more),
								font('bold', 'Не указано' if not self.client.withdraw else self.client.withdraw),
								font('bold', self.user.star),
								font('bold', self.user.assessment),
								font('bold', self.user.count_work)
							)

				self.answer += font('light', 'Для изменения информации нажимайте на кнопки\nНажмите {}, чтобы сохранить изменение'.format(font('bold', '«‎Применить»')))
				keyboard = types.InlineKeyboardMarkup(True)

				buttons = []
				buttons.append({'text': 'Имя', 'callback_data': 'USER100'})
				buttons.append({'text': 'Город', 'callback_data': 'USER101'})
				buttons.append({'text': 'Подробнее', 'callback_data': 'USER102'})
				buttons.append({'text': 'Вывод', 'callback_data': 'USER103'})

				keyboard.keyboard = constructor(buttons, self.COUNT_ROW)

				if(data):
					try:
						self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=data.message.message_id, parse_mode="HTML", text=self.answer, reply_markup=keyboard)
					except:
						pass
				else:
					self.telegram_bot.send_message(chat_id=self.client.chat_id, text=self.answer, parse_mode='HTML', reply_markup=keyboard)

			elif(message == 'категории 🗂'):
				self.answer = '{}\n{}'.format(font('bold', '🗂 Обновление категорий'), font('light', '✏️ Выберите предмет, который хотите добавить/удалить'))
				keyboard = types.InlineKeyboardMarkup(True)

				buttons = []
				subject_class = SubjectClass()
				for x in subject_class.subjects.filter(level=1):
					buttons.append({'text': x.name, 'callback_data': 'SUBJECT100_{}_1_{}'.format(x.id, x.id)})

				keyboard.keyboard = constructor(buttons, self.COUNT_ROW)
				self.telegram_bot.send_message(chat_id=self.client.chat_id, text=self.answer, parse_mode='HTML', reply_markup=keyboard)

			elif(message == 'меню помощника 🎓'):
				self.answer = 'Меню помощника'
				use_buttons = self.buttons_executor
				keyboard = types.ReplyKeyboardMarkup(True)
				keyboard.keyboard = constructor(use_buttons, self.COUNT_ROW)
				self.telegram_bot.send_message(chat_id=self.client.chat_id, text=self.answer, parse_mode='HTML', reply_markup=keyboard)
			# elif(message in ['исполнитель', 'заказчик']):
			# 	if('исполнитель' in message):
			# 		self.answer = 'Меню исполнителя'
			# 		use_buttons = self.buttons_executor
			# 	else:
			# 		self.answer = 'Меню заказчика'
			# 		use_buttons = self.buttons_customer

			# 	keyboard = types.ReplyKeyboardMarkup(True)
			# 	f = lambda A, n: [A[i:i+n] for i in range(0, len(A), n)]
			# 	keyboard.keyboard = f(use_buttons, self.COUNT_ROW)
			# 	self.telegram_bot.send_message(chat_id=self.client.chat_id, text=self.answer, parse_mode='HTML', reply_markup=keyboard)

			elif(message == 'мой баланс 💰'):
				self.user.withdrawal_list()
				self.answer = 'Ваш баланс: {}\nОжидается на вывод: {}'.format(font('bold', '{} грн'.format(math.ceil(self.client.balance))), font('bold', '{} грн'.format(math.ceil(self.user.withdrawal_sum['amount_two__sum'] if self.user.withdrawal_sum['amount_two__sum'] else 0))))
				buttons = []
				buttons.append({'text': 'Пополнить', 'callback_data': 'BALANCE100'})
				buttons.append({'text': 'Вывести', 'callback_data': 'BALANCE101'})
				buttons.append({'text': 'Рефералка', 'callback_data': 'BALANCE120'})

				keyboard = types.InlineKeyboardMarkup(True)
				keyboard.keyboard = constructor(buttons, self.COUNT_ROW)
				self.telegram_bot.send_message(chat_id=self.client.chat_id, text=self.answer, parse_mode='HTML', reply_markup=keyboard)

			elif(message == 'новый заказ ➕'):
				self.answer = font('bold', 'Постановка заказа\n')
				self.answer += font('light', '✏️ Выберите интересующий вас предмет')
				keyboard = types.InlineKeyboardMarkup(True)

				buttons = []
				subject_class = SubjectClass()
				for x in subject_class.subjects.filter(level=1):
					buttons.append({'text': x.name, 'callback_data': 'CUSTOMER100_{}_1_{}'.format(x.id, x.id)})

				keyboard.keyboard = constructor(buttons, self.COUNT_ROW)
				self.telegram_bot.send_message(chat_id=self.client.chat_id, text=self.answer, parse_mode='HTML', reply_markup=keyboard)
			
			elif(message == 'найти заказ 🔍'):
				task = TaskClass(self.client, 'EXECUTOR')
				task.select_task()

				if(data):
					self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=data.message.message_id, parse_mode="HTML", text=task.answer, reply_markup=task.keyboard)
				else:
					self.telegram_bot.send_message(chat_id=self.client.chat_id, text=task.answer, parse_mode='HTML', reply_markup=task.keyboard)

			elif(message == 'мои заказы 📝'):
				task = TaskClass(self.client, 'CUSTOMERSEARCH')
				task.select_task()
				if(data):
					self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=data.message.message_id, parse_mode="HTML", text=task.answer, reply_markup=task.keyboard)
				else:
					self.telegram_bot.send_message(chat_id=self.client.chat_id, text=task.answer, parse_mode='HTML', reply_markup=task.keyboard)
			
			elif(message == 'мои заказы 👨'):
				task = TaskClass(self.client, 'EXECUTORSEARCH')
				task.select_task()
				if(data):
					self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=data.message.message_id, parse_mode="HTML", text=task.answer, reply_markup=task.keyboard)
				else:
					self.telegram_bot.send_message(chat_id=self.client.chat_id, text=task.answer, parse_mode='HTML', reply_markup=task.keyboard)

			elif(message == 'помощь 💻'):
				self.answer = 'Пожалуйста, опишите то, что случилось @Viktor_Rachuk\n\n' + SUPPORT_TEXT
				self.telegram_bot.send_message(chat_id=self.client.chat_id, text=self.answer, parse_mode='HTML', disable_web_page_preview=True)

			elif(message == 'назад ↩️'):
				self.quick_response('/start', data)

			elif(message == '/info'):
				self.telegram_bot.send_message(chat_id=self.client.chat_id, text=INFO_TEXT, parse_mode='HTML')

			else:
				self.answer = 'Я вас не понимаю ☹️'
				self.telegram_bot.send_message(chat_id=self.client.chat_id, text=self.answer, parse_mode='HTML')
		
		elif(self.telegram_bot.get_me().username == 'ShpargalochkaCab_bot'):
			task = TaskClass(self.client, 'CABINET')
			if(task.task):
				if(message in str(self.buttons_cabinetcustomer).lower() or message in str(self.buttons_cabinetexecutor).lower() or message in ['/start','/info']):
					self.user.role_task()
					if(message == '/start'):
						self.answer = 'Главное меню'
						keyboard = types.ReplyKeyboardMarkup(True)
						self.user.role_task()
						if(self.user.role == 'customer'): keyboard.keyboard = constructor(self.buttons_cabinetcustomer, self.COUNT_ROW)
						elif(self.user.role == 'executor'): keyboard.keyboard = constructor(self.buttons_cabinetexecutor, self.COUNT_ROW)
						self.telegram_bot.send_message(chat_id=self.client.chat_id, text=self.answer, parse_mode='HTML', reply_markup=keyboard)

					elif(message == '/info'):
						self.answer = 'Информация'
						self.telegram_bot.send_message(chat_id=self.client.chat_id, text=self.answer, parse_mode='HTML')
					
					elif(message == 'показать заказ 🔖'):
						task.show_task()
						self.telegram_bot.send_message(chat_id=self.client.chat_id, text=task.answer, parse_mode='HTML', reply_markup=task.keyboard)

					elif(message == 'история 💬'):
						task.message_list()
						self.telegram_bot.send_message(chat_id=self.client.chat_id, text=task.answer, parse_mode='HTML')

					elif(message == 'навигация 🕸'):
						task.task_list()
						self.telegram_bot.send_message(chat_id=self.client.chat_id, text=task.answer, parse_mode='HTML', reply_markup=task.keyboard)

					elif(message == 'завершить заказ ☑️' and self.user.role == 'executor'):
						self.answer = font('bold', 'Вы действительно хотите завершить заказ #{}?\n'.format(task.task.id))
						self.answer += font('light', '⚠️ У заказчика начнется гарантийный период 10 дней на протяжение которых, он может запросить у вас корректировку работы')
						buttons = []
						buttons.append({'text': 'Да ✅', 'callback_data': 'CABINET110_{}_{}'.format(task.cabinet.id, 'yes')})
						buttons.append({'text': 'Нет ❌', 'callback_data': 'USER888'})
						self.keyboard = types.InlineKeyboardMarkup(True)
						self.keyboard.keyboard = constructor(buttons, 1)
						self.telegram_bot.send_message(chat_id=self.client.chat_id, text=self.answer, parse_mode='HTML', reply_markup=self.keyboard)
				else:
					if(not self.len_string(message, 500)):
						self.telegram_bot.send_message(chat_id=self.client.chat_id, text=self.answer, parse_mode='HTML', reply_markup=self.keyboard_cancel)
						return

					task.message_cabinet(message)
					if(task.answer): self.telegram_bot.send_message(chat_id=task.chat_id, text=task.answer, parse_mode='HTML')
			else:
				task.task_list()
				if(task.keyboard.keyboard):
					text = 'Выберите задачу'
					self.telegram_bot.send_message(chat_id=self.client.chat_id, text=text, parse_mode='HTML', reply_markup=task.keyboard)
				else:
					text = 'Задач в разработке не найдено'
					self.telegram_bot.send_message(chat_id=self.client.chat_id, text=text, parse_mode='HTML')
	
	def callback_response(self, data, call='outside'):
		if(call == 'inside'):
			step = data['step']
			message_id = data['message_id']
		else:
			step = data.data
			message_id = data.message.message_id
		print(199,step.split('_'))
		# if(self.telegram_bot.get_me().username == 'autotextbackbot'):
		if('USER' in step):
			if(step == 'USER777'):
				self.quick_response('профиль 📖', data)
				self.delete_dialog = True

			elif(step == 'USER888'):
				self.answer = 'Действие отменено'
				self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=message_id, parse_mode="HTML", text=self.answer)
				self.delete_dialog = True

			elif(step == 'USER100'):
				self.answer = 'Введите ваше имя'
				self.data_dialog = step + '|' + str(message_id)
				self.telegram_bot.send_message(chat_id=self.client.chat_id, parse_mode="HTML", text=self.answer, reply_markup=self.keyboard_cancel)

			elif(step == 'USER101'):
				self.answer = 'Введите ваш город'
				self.data_dialog = step + '|' + str(message_id)
				self.telegram_bot.send_message(chat_id=self.client.chat_id, parse_mode="HTML", text=self.answer, reply_markup=self.keyboard_cancel)

			elif(step == 'USER102'):
				self.answer = 'Введите информацию о себе'
				self.data_dialog = step + '|' + str(message_id)
				self.telegram_bot.send_message(chat_id=self.client.chat_id, parse_mode="HTML", text=self.answer, reply_markup=self.keyboard_cancel)
			
			elif(step == 'USER103'):
				self.answer = 'Введите через пробел ФИО владельца карты и номер карты'
				self.data_dialog = step + '|' + str(message_id)
				self.telegram_bot.send_message(chat_id=self.client.chat_id, parse_mode="HTML", text=self.answer, reply_markup=self.keyboard_cancel)
	
		elif('BALANCE' in step):
			if(step == 'BALANCE100'):
				self.answer += 'Если согласны с условиями {}, введите {}, на которую хотите пополнить баланс (от 10 до 5000 грн)\n'.format(font('bold', '<a href="#">пользовательского соглашения</a>'), font('bold', 'сумму'))
				self.data_dialog = 'BALANCE100' + '|' + str(message_id)
				self.telegram_bot.send_message(chat_id=self.client.chat_id, parse_mode="HTML", text=self.answer, reply_markup=self.keyboard_cancel, disable_web_page_preview=True)
			elif(step == 'BALANCE101'):
				if(not self.client.withdraw):
					self.answer = 'Для начала нужно заполнить данные о Выводе в вашем профиле'
					self.telegram_bot.send_message(chat_id=self.client.chat_id, text=self.answer, parse_mode='HTML', reply_markup=self.keyboard_cancel)
					return

				self.answer = 'Введите сумму, которую хотите вывести (*от 10 до 1000 грн*)'
				self.data_dialog = 'BALANCE101' + '|' + str(message_id)
				self.telegram_bot.send_message(chat_id=self.client.chat_id, parse_mode="HTML", text=self.answer, reply_markup=self.keyboard_cancel)
			elif(step == 'BALANCE120'):
				buttons = []
				self.answer = ''
				if(not self.client.refer):
					self.answer += REFERAL_TEXT
					buttons.append({'text': 'Ввести код', 'callback_data': 'BALANCE121'})
				buttons.append({'text': 'Показать код', 'callback_data': 'BALANCE122'})

				keyboard = types.InlineKeyboardMarkup(True)
				keyboard.keyboard = constructor(buttons, self.COUNT_ROW)
				self.telegram_bot.send_message(chat_id=self.client.chat_id, text=self.answer, parse_mode='HTML', reply_markup=keyboard)

			elif(step == 'BALANCE121'):
				self.answer = 'Введите реферальный код'
				self.telegram_bot.send_message(chat_id=self.client.chat_id, parse_mode="HTML", text=self.answer, reply_markup=self.keyboard_cancel)
				self.data_dialog = 'BALANCE121' + '|' + str(message_id)
				

			elif(step == 'BALANCE122'):
				self.answer = self.client.refer_code
				self.telegram_bot.send_message(chat_id=self.client.chat_id, parse_mode="HTML", text=self.answer)

		elif('EXECUTOR' in step or 'CUSTOMERSEARCH' in step or 'FEEDBACK' in step):
			first_data = step.split('_')[1]
			print(367, step)
			if('EXECUTOR100' in step or 'EXECUTOR110' in step or 'CUSTOMERSEARCH110' in step):
				id_task = first_data
				if('EXECUTOR100' in step):
					self.delete_dialog = True
					task = TaskClass(self.client, 'EXECUTOR', id_task)
					task.show_task()
				elif('EXECUTOR110' in step):
					task = TaskClass(self.client, 'EXECUTOR', id_task)
					task.show_task(search=True)
				elif('CUSTOMERSEARCH110' in step):
					task = TaskClass(self.client, 'CUSTOMERSEARCH', id_task)
					task.show_task(search=True)
				if(task.task):
					self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=message_id, parse_mode="HTML", text=task.answer, reply_markup=task.keyboard)
				# else:
				# 	self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=message_id, parse_mode="HTML", text=task.answer)

			elif('EXECUTOR999' in step):
				id_task = first_data
				task = TaskClass(self.client, 'EXECUTOR', id_task)
				self.keyboard = types.InlineKeyboardMarkup(True)
				self.keyboard.keyboard.append([{'text': 'Подробнее', 'callback_data': 'EXECUTOR100_' + str(id_task)}])
				self.answer = '💣 Новый заказ: {} ({})'.format(font('bold', '#{} {}'.format(task.task.id, task.task.subject.name)), (task.task.more[:20] + '...') if len(task.task.more) > 20 else task.task.more)
				self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=message_id, parse_mode="HTML", text=self.answer, reply_markup=self.keyboard)

			elif('EXECUTOR101' in step):
				id_task = first_data
				task = TaskClass(self.client, 'EXECUTOR', id_task)
				if(task.task.files.all()):
					for x in task.task.files.all():
						self.telegram_bot.send_document(self.client.chat_id, x.upload)
				else:
					answer = 'Нет прикрепленных файлов'
					self.telegram_bot.send_message(chat_id=self.client.chat_id, parse_mode="HTML", text=answer)

			elif('EXECUTOR120' in step):
				id_task = first_data
				self.delete_dialog = True
				self.answer += 'Укажите цену'
				self.keyboard = types.InlineKeyboardMarkup(True)
				if('search' in step): search = True
				else: search = False
				self.keyboard.keyboard.append([{'text': 'Отменить ❌', 'callback_data': search_list[search]['callback_data'] + str(id_task)}])
				self.telegram_bot.delete_message(chat_id=self.client.chat_id, message_id=message_id)
				mes = self.telegram_bot.send_message(chat_id=self.client.chat_id, parse_mode="HTML", text=self.answer, reply_markup=self.keyboard)
				self.data_dialog = 'EXECUTOR120' + '|' + str(mes.message_id) + '|' + id_task + '|' + search_list[search]['postfix']

			elif('EXECUTOR130' in step):
				id_task = first_data
				self.delete_dialog = True
				self.answer = 'Пришлите комментарий к заданию, который заказчик увидит в Вашей заявке'
				self.keyboard = types.InlineKeyboardMarkup(True)

				if('search' in step): search = True
				else: search = False

				self.keyboard.keyboard.append([{'text': 'Назад ↩️', 'callback_data': 'EXECUTOR120_' + id_task + search_list[search]['postfix']}])
				self.keyboard.keyboard.append([{'text': 'Отменить ❌', 'callback_data': search_list[search]['callback_data'] + str(id_task)}])
				self.telegram_bot.delete_message(chat_id=self.client.chat_id, message_id=message_id)
				mes = self.telegram_bot.send_message(chat_id=self.client.chat_id, parse_mode="HTML", text=self.answer, reply_markup=self.keyboard)
				self.data_dialog = 'EXECUTOR130' + '|' + str(mes.message_id) + '|' + id_task + '|' + search_list[search]['postfix']

			elif('EXECUTOR140' in step):
				id_task = first_data
				self.delete_dialog = True

				task = TaskClass(self.client, 'CUSTOMERSEARCH', id_task)
				task.update_feedback(action='active')

				self.delete_dialog = True
				self.quick_response('найти заказ 🔍', data)
				# self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=message_id, parse_mode="HTML", text=task.answer, reply_markup=task.keyboard)

			elif('EXECUTOR150' in step):
				id_task = first_data
				type_call = step.split('_')[2]
				task = TaskClass(self.client, 'EXECUTORSEARCH', id_task)
				task.show_task()
				if(type_call == 'inside'): task.keyboard.keyboard.append([{'text': 'Назад ↩️', 'callback_data': 'EXECUTOR170____'}])
				self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=message_id, parse_mode="HTML", text=task.answer, reply_markup=task.keyboard)

			elif('EXECUTOR160' in step):
				id_task = first_data
				answer = step.split('_')[2]
				task = TaskClass(self.client, 'EXECUTORSEARCH', id_task)
				if(answer == 'yes'):
					task.update_feedback(action='accept')
					if(not task.state): 
						self.answer = 'Действие уже выполнено'
						self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=message_id, parse_mode='HTML', text=self.answer)
						return

					self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=message_id, parse_mode="HTML", text=task.answer, reply_markup=task.keyboard_executor)
					self.telegram_bot.send_message(chat_id=task.chat_id, parse_mode="HTML", text=task.answer_customer, reply_markup=task.keyboard_customer)
				elif(answer == 'no'):
					task.update_feedback(action='cancel')
					if(not task.state): 
						self.answer = 'Действие уже выполнено'
						self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=message_id, parse_mode='HTML', text=self.answer)
						return

					self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=message_id, parse_mode="HTML", text=task.answer, reply_markup=task.keyboard)
					self.telegram_bot.send_message(chat_id=task.chat_id, parse_mode="HTML", text=task.answer_customer)

			elif('EXECUTOR170' in step):
				self.quick_response('мои заказы 👨', data)

			elif('EXECUTOR888' in step):
				self.quick_response('найти заказ 🔍', data)
			
			elif('EXECUTORPAGE' in step or 'CUSTOMERSEARCHPAGE' in step or 'FEEDBACKPAGE' in step or 'EXECUTORSEARCHPAGE' in step):
				page = first_data
				if('EXECUTORPAGE' in step):
					task = TaskClass(self.client, 'EXECUTOR')
					task.select_task(page=page)
				elif('EXECUTORSEARCHPAGE' in step):
					task = TaskClass(self.client, 'EXECUTORSEARCH')
					task.select_task(page=page)
				elif('CUSTOMERSEARCHPAGE' in step):
					task = TaskClass(self.client, 'CUSTOMERSEARCH')
					task.select_task(page=page)
				elif('FEEDBACKPAGE' in step):
					second_data = step.split('_')[2]
					id_task = second_data
					task = TaskClass(self.client, 'CUSTOMERSEARCH', id_task)
					task.task_feedback(page=page)
				self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=message_id, text=task.answer, parse_mode='HTML', reply_markup=task.keyboard)

			elif('CUSTOMERSEARCH120' in step):
				id_task = first_data
				self.delete_dialog = True
				self.answer += '‼️ При редактировании заказа {} все ставки помощников.\nВы уверены, что хотите внести изменения?\n'.format(font('bold', 'сбросятся'))
				self.answer += '{} ✅ - укажите описание\n'.format(font('bold', 'Да'))
				self.answer += '{} ❌ - нажмите {}'.format(font('bold', 'Нет'), font('light', font('bold', '«Отменить ❌»')))
				self.data_dialog = 'CUSTOMERSEARCH120' + '|' + str(message_id) + '|' + id_task
				self.keyboard = types.InlineKeyboardMarkup(True)
				self.keyboard.keyboard.append([{'text': 'Отменить ❌', 'callback_data': 'CUSTOMERSEARCH110_' + id_task}])
				self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=message_id, parse_mode="HTML", text=self.answer, reply_markup=self.keyboard)

			elif('CUSTOMERSEARCH130' in step):
				id_task = first_data
				self.delete_dialog = True
				task = TaskClass(self.client, 'CUSTOMERSEARCH', id_task)
				self.answer += '‼️ При редактировании заказа {} все ставки помощников.\nВы уверены, что хотите внести изменения?\n'.format(font('bold', 'сбросятся'))
				self.answer += '{} ✅ - прикрепите файл\n'.format(font('bold', 'Да'))
				self.answer += '{} ❌ - нажмите {}'.format(font('bold', 'Нет'), font('light', font('bold', '«Отменить ❌»')))
				self.data_dialog = 'CUSTOMERSEARCH130' + '|' + str(message_id) + '|' + id_task + '|first'
				self.keyboard = types.InlineKeyboardMarkup(True)
				self.keyboard.keyboard.append([{'text': 'Отменить ❌', 'callback_data': 'CUSTOMERSEARCH110_' + id_task}])
				self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=message_id, parse_mode="HTML", text=self.answer, reply_markup=self.keyboard)

			elif('CUSTOMERSEARCH140' in step):
				id_task = first_data
				self.delete_dialog = True
				self.callback_response({'step': 'CUSTOMERSEARCH110_' + id_task, 'message_id': message_id}, 'inside')

			elif('CUSTOMERSEARCH150' in step):
				id_task = first_data
				self.delete_dialog = True
				task = TaskClass(self.client, 'CUSTOMERSEARCH', id_task)
				task.task_feedback()
				self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=message_id, parse_mode="HTML", text=task.answer, reply_markup=task.keyboard)

			elif('CUSTOMERSEARCH160' in step):
				id_task = first_data
				buttons = []
				keyboard = types.InlineKeyboardMarkup(True)
				self.answer = 'Вы {} хотите удалить заказ?'.format(font('bold', 'действительно'))
				buttons.append({'text': 'Да ✅', 'callback_data': 'CUSTOMERSEARCH161_' + str(id_task) + '_____'})
				buttons.append({'text': 'Нет ❌', 'callback_data': 'CUSTOMERSEARCH110_' + str(id_task) + '____'})
				keyboard.keyboard = constructor(buttons, self.COUNT_ROW)
				self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=message_id, parse_mode="HTML", text=self.answer, reply_markup=keyboard)
			
			elif('CUSTOMERSEARCH161' in step):
				id_task = first_data
				task = TaskClass(self.client, 'CUSTOMERSEARCH', id_task)
				task.delete_task()
				self.quick_response('мои заказы 📝', data)

			elif('CUSTOMERSEARCH170' in step):
				self.quick_response('мои заказы 📝', data)


		elif('SUBJECT' in step or 'CUSTOMER' in step):
			subject_id = step.split('_')[1]
			page = step.split('_')[2]
			parent_id = step.split('_')[3]
			if('SUBJECT' in step): self.answer = '{}\n{}'.format(font('bold', '🗂 Обновление категорий'), font('light', '✏️ Выберите предмет, который хотите добавить/удалить'))
			elif('CUSTOMER' in step): self.answer = '{}\n{}'.format(font('bold', '📒 Постановка заказа'), font('light', '✏ Выберите интересующий вас предмет'))
			
			print(step)
			if('100PAGE' in step):
				buttons = []
				subject_class = SubjectClass()
				obj = subject_class.subjects.filter(id=int(parent_id))[0]
				parent = subject_class.subjects.filter(next_subject=obj)
				if(not parent): parent = obj
				else: parent = parent[0]
				subjects = obj.next_subject.all()
				if(subjects):
					if('SUBJECT' in step): subject_class.generate_buttons(self.client, subjects, subject_id, page, parent.id, 'SUBJECT100')
					elif('CUSTOMER' in step): subject_class.generate_buttons(self.client, subjects, subject_id, page, parent.id, 'CUSTOMER100')
					# self.telegram_bot.send_message(chat_id=self.client.chat_id, text=self.answer, parse_mode='HTML', reply_markup=subject_class.keyboard)
					self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=message_id, parse_mode="HTML", text=self.answer, reply_markup=subject_class.keyboard)

			elif('100BACK' in step):
				buttons = []
				subject_class = SubjectClass()
				obj = subject_class.subjects.filter(id=int(parent_id))[0]
				parent = subject_class.subjects.filter(next_subject=obj)
				if(not parent): 
					subjects = subject_class.subjects.filter(level=obj.level)
					parent = obj
				else: 
					parent = parent[0]
					subjects = parent.next_subject.all()
				print(275,subject_id)
				print(275,parent)
				print(275,obj)
				print(275,subjects)
				if(subjects):
					if(obj.level == 1):
						if('SUBJECT' in step): subject_class.generate_buttons(self.client, subjects, subject_id, page, parent.id, 'SUBJECT100', back=True, paginator=False)
						elif('CUSTOMER' in step): subject_class.generate_buttons(self.client, subjects, subject_id, page, parent.id, 'CUSTOMER100', back=True, paginator=False)
					else:
						if('SUBJECT' in step): subject_class.generate_buttons(self.client, subjects, subject_id, page, parent.id, 'SUBJECT100', back=True)
						elif('CUSTOMER' in step): subject_class.generate_buttons(self.client, subjects, subject_id, page, parent.id, 'CUSTOMER100', back=True)

				# self.telegram_bot.send_message(chat_id=self.client.chat_id, text=self.answer, parse_mode='HTML', reply_markup=subject_class.keyboard)
				self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=message_id, parse_mode="HTML", text=self.answer, reply_markup=subject_class.keyboard)

			elif('CUSTOMER110' in step):
				self.delete_dialog = True
				task = TaskClass(self.client)
				task.update_task('create')
				self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=message_id, parse_mode="HTML", text=task.answer, reply_markup=task.keyboard)
			
			elif('CUSTOMER111' in step):
				self.delete_dialog = True
				task = TaskClass(self.client)
				task.update_task(action='deadline', message=subject_id)
				# self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=message_id, parse_mode="HTML", text=task.answer, reply_markup=task.keyboard)
				self.answer = '⏰ Срок сдачи до: {}\n'.format(font('bold', task.answer))
				self.answer += font('light', '📋 Максимально подробно {} задание'.format(font('bold', 'опишите')))
				self.data_dialog = 'CUSTOMER120' + '|' + str(message_id)
				self.keyboard_cancel.keyboard.append([{'text': 'Назад ↩️', 'callback_data': 'CUSTOMER110____'}])
				self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=message_id, parse_mode="HTML", text=self.answer, reply_markup=self.keyboard_cancel)

			elif('CUSTOMER112' in step):
				self.delete_dialog = True
				task = TaskClass(self.client)
				task.calendar()
				self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=message_id, parse_mode="HTML", text=task.answer, reply_markup=task.keyboard)

			elif('CUSTOMER113' in step):
				self.delete_dialog = True
				task = TaskClass(self.client)
				task.calendar(month=int(subject_id), year=int(page))
				self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=message_id, parse_mode="HTML", text=task.answer, reply_markup=task.keyboard)

			elif('CUSTOMER120' in step):
				self.delete_dialog = True
				task = TaskClass(self.client)
				self.answer = '⏰ Срок сдачи до: {}\n'.format(font('bold', datetime.date(task.task.deadline)))
				self.answer += font('light','📋 Максимально подробно {} задание'.format(font('bold', 'опишите')))
				self.data_dialog = 'CUSTOMER120' + '|' + str(message_id)
				self.keyboard_cancel.keyboard.append([{'text': 'Назад ↩️', 'callback_data': 'CUSTOMER110____'}])
				self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=message_id, parse_mode="HTML", text=self.answer, reply_markup=self.keyboard_cancel)

			elif('CUSTOMER130' in step):
				task = TaskClass(self.client)
				task.task.files.clear()
				self.delete_dialog = True
				self.answer = '📋 Описание заказа: {}\n'.format(font('bold',task.task.more))
				self.answer += font('light', '📎 Пришлите остальные {}, касающиеся задания. Это могут быть файлы и/или фото'.format(font('bold', 'материалы')))
				self.data_dialog = 'CUSTOMER130' + '|' + str(message_id)
				self.keyboard_cancel.keyboard.append([{'text': 'Пропустить', 'callback_data': 'CUSTOMER140____'}])
				self.keyboard_cancel.keyboard.append([{'text': 'Назад ↩️', 'callback_data': 'CUSTOMER120____'}])
				self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=message_id, parse_mode="HTML", text=self.answer, reply_markup=self.keyboard_cancel)
			
			elif('CUSTOMER140' in step):
				self.delete_dialog = True
				task = TaskClass(self.client)
				task.check_task()
				self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=message_id, parse_mode="HTML", text=task.answer, reply_markup=task.keyboard)

			elif('CUSTOMER150' in step):
				self.delete_dialog = True
				task = TaskClass(self.client)
				task.create()
				self.answer = font('bold', '✅ Поздравляем, помощники уже изучают ваш заказ 🔎#{}\n'.format(task.task.id))
				self.answer += font('light', '👇 Можете посмотреть и изменить его в {}'.format(font('bold', '«Мои заказы 📝»')))
				self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=message_id, parse_mode="HTML", text=self.answer)

			elif('CUSTOMER160' in step):
				self.delete_dialog = True
				task = TaskClass(self.client)
				task.show_feedback(subject_id)
				if(page == 'inside'): task.keyboard.keyboard.append([{'text': 'Назад ↩️', 'callback_data': 'CUSTOMERSEARCH150_' + str(task.task.id)}])
				else: task.keyboard.keyboard.append([{'text': 'Скрыть', 'callback_data': 'CUSTOMER190_' + subject_id + '____'}])
				self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=message_id, parse_mode="HTML", text=task.answer, reply_markup=task.keyboard)

			elif('CUSTOMER170' in step):
				self.delete_dialog = True
				task = TaskClass(self.client)
				task.payment_feedback(subject_id)
				self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=message_id, parse_mode="HTML", text=task.answer, reply_markup=task.keyboard)

			elif('CUSTOMER171' in step):
				buttons = []
				keyboard = types.InlineKeyboardMarkup(True)
				self.answer = 'Вы {} хотите удалить заявку?'.format(font('bold', 'действительно'))
				buttons.append({'text': 'Да ✅', 'callback_data': 'CUSTOMER172_' + str(subject_id) + '_____'})
				buttons.append({'text': 'Нет ❌', 'callback_data': 'CUSTOMER160_' + str(subject_id) + '_inside___'})
				keyboard.keyboard = constructor(buttons, self.COUNT_ROW)
				self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=message_id, parse_mode="HTML", text=self.answer, reply_markup=keyboard)

			elif('CUSTOMER172' in step):
				self.delete_dialog = True
				task = TaskClass(self.client)
				task.refuse_feedback(subject_id)
				if(task.state):
					self.telegram_bot.send_message(chat_id=task.feedback.client.chat_id, parse_mode="HTML", text=task.answer)
					self.callback_response({'step': 'CUSTOMERSEARCH150_' + str(task.feedback.task.id), 'message_id': message_id}, 'inside')
				else:
					self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=message_id, parse_mode="HTML", text=task.answer)

			elif('CUSTOMER180' in step):
				self.delete_dialog = True
				task = TaskClass(self.client)
				task.accept_feedback(subject_id)
				if(task.state):
					if('недостаточно' in task.answer):
						self.telegram_bot.send_message(chat_id=self.client.chat_id, parse_mode="HTML", text=task.answer)
						self.quick_response('мой баланс 💰')
					else:
						self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=message_id, parse_mode="HTML", text=task.answer)
				else:
					self.answer = 'Действие уже выполнено'
					self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=message_id, parse_mode='HTML', text=self.answer)

			elif('CUSTOMER190' in step):
				self.delete_dialog = True
				task = TaskClass(self.client)
				task.preview_feedback(subject_id)
				self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=message_id, parse_mode="HTML", text=task.answer, reply_markup=task.keyboard)

			elif('CUSTOMER200' in step):
				self.delete_dialog = True
				self.keyboard = types.InlineKeyboardMarkup(True)
				self.keyboard.keyboard.append([{'text': 'Отменить ❌', 'callback_data': 'CUSTOMER160_' + str(subject_id) + '_____'}])
				self.answer = '{}\n{} {}'.format(font('bold', 'Введите текст сообщения'), font('light', 'Вы можете вводить его то тех пор, пока не нажмёте'), font('bold', '«Отправить 📨»'))
				self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=message_id, parse_mode="HTML", text=self.answer, reply_markup=self.keyboard)
				self.data_dialog = 'CUSTOMER200' + '|' + str(message_id) + '|' + subject_id + '|' + page

			elif('CUSTOMER210' in step):
				self.delete_dialog = True
				task = TaskClass(self.client)
				task.send_message(subject_id, page)
				self.telegram_bot.send_message(chat_id=task.chat_id, parse_mode="HTML", text=task.answer, reply_markup=task.keyboard)
				if(page == 'executor'):
					self.callback_response({'step': 'CUSTOMER160_' + str(subject_id) + '_____', 'message_id': message_id}, 'inside')
					self.telegram_bot.send_message(chat_id=self.client.chat_id, parse_mode="HTML", text='Сообщение отправлено')
				else:
					self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=message_id, parse_mode="HTML", text='Сообщение отправлено')

			elif('CUSTOMER888' in step):
				self.delete_dialog = True
				task = TaskClass(self.client)
				if(page == 'customer'): 
					self.callback_response({'step': 'CUSTOMER160_' + str(subject_id) + '_____', 'message_id': message_id}, 'inside')
					return
				elif(page == 'executor'): task.send_message(subject_id, page, 'inside')
				self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=message_id, parse_mode='HTML', text=task.answer, reply_markup=task.keyboard)

			elif('SUBJECT100' in step or 'CUSTOMER100' in step):
				buttons = []
				keyboard = ''
				subject_class = SubjectClass()
				obj = subject_class.subjects.filter(id=int(subject_id))[0]
				parent = subject_class.subjects.filter(next_subject=obj)
				if(not parent): parent = obj
				else: parent = parent[0]
				subjects = obj.next_subject.all()
				if(subjects):
					if('SUBJECT' in step): subject_class.generate_buttons(self.client, subjects, subject_id, 1, parent.id, 'SUBJECT100')
					elif('CUSTOMER' in step): subject_class.generate_buttons(self.client, subjects, subject_id, 1, parent.id, 'CUSTOMER100')
					keyboard = subject_class.keyboard
				else:
					if('SUBJECT' in step):
						subject_class.update_filter(self.client, obj)
						subject_class.generate_buttons(self.client, subject_class.subjects.filter(next_subject=obj)[0].next_subject.all(), subject_id, page, parent.id, 'SUBJECT100')
						keyboard = subject_class.keyboard
					elif('CUSTOMER' in step): 
						task = TaskClass(self.client)
						task.update_task('create', subject=obj)
						self.answer = task.answer
						keyboard = task.keyboard
				# self.telegram_bot.send_message(chat_id=self.client.chat_id, text=self.answer, parse_mode='HTML', reply_markup=subject_class.keyboard)
				self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=message_id, parse_mode="HTML", text=self.answer, reply_markup=keyboard)

		if(self.telegram_bot.get_me().username == 'ShpargalochkaCab_bot'):
			if('CABINET' in step):
				task = TaskClass(self.client, 'CABINET')
				cabinet_id = step.split('_')[1]
				cabinet = Cabinet.objects.filter(id=cabinet_id)[0]
				if('CABINET100' in step):
					# task = TaskClass(self.client, 'CABINET')
					task.task_active(cabinet_id)
					if(task.state):
						if(task.answer): self.telegram_bot.send_message(chat_id=task.chat_id, text=task.answer, parse_mode='HTML')
						task.task_list()
						self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, text=task.answer, parse_mode='HTML', message_id=message_id, reply_markup=task.keyboard)
					else:
						self.answer = 'Действие уже выполнено'
						self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=message_id, parse_mode='HTML', text=self.answer)

					return

				if(task.task):
					print(task.task.id, cabinet.task.id)
					if(task.task.id != cabinet.task.id):
						self.answer = 'Перейдите в кабинет с заказом ' + font('bold', '#{}'.format(cabinet.task.id))
						self.telegram_bot.send_message(chat_id=self.client.chat_id, text=self.answer, parse_mode='HTML')
						return
					if('CABINET110' in step):
						task.exit_cabinet(step.split('_')[2])
						if(task.state):
							self.telegram_bot.delete_message(chat_id=self.client.chat_id, message_id=message_id)
							if(step.split('_')[2] == 'no'):
								self.telegram_bot.send_message(chat_id=task.chat_id, text=task.answer, parse_mode='HTML')
						else:
							self.answer = 'Действие уже выполнено'
							self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=message_id, parse_mode='HTML', text=self.answer)

					elif('CABINET12' in step):
						if('CABINET121' in step):
							task.task_grade(type_grade='one', ball=step.split('_')[3], role=step.split('_')[2])
							if(not task.state):
								return
							task.get_type_grade(cabinet_id=cabinet_id, type_grade='two', role=step.split('_')[2])
							self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, text=task.answer, parse_mode='HTML', message_id=message_id, reply_markup=task.keyboard)

						elif('CABINET122' in step):
							task.task_grade(type_grade='two', ball=step.split('_')[3], role=step.split('_')[2])
							if(not task.state):
								return
							task.get_type_grade(cabinet_id=cabinet_id, type_grade='three', role=step.split('_')[2])
							self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, text=task.answer, parse_mode='HTML', message_id=message_id, reply_markup=task.keyboard)

						elif('CABINET123' in step):
							task.task_grade(type_grade='three', ball=step.split('_')[3], role=step.split('_')[2])
							if(not task.state):
								return
							task.get_type_grade(cabinet_id=cabinet_id, type_grade='four', role=step.split('_')[2])
							self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, text=task.answer, parse_mode='HTML', message_id=message_id, reply_markup=task.keyboard)

						elif('CABINET124' in step):
							task.task_grade(type_grade='four', ball=step.split('_')[3], role=step.split('_')[2])
							if(not task.state):
								return
							task.get_type_grade(cabinet_id=cabinet_id, type_grade='two', role=step.split('_')[2])
							self.answer = 'Спасибо за оценку, какой ' + font('bold', 'отзыв') + ' вы бы оставили о помощнике?'
							self.keyboard = types.InlineKeyboardMarkup(True)
							self.keyboard.keyboard.append([{'text': 'Пропустить', 'callback_data': 'CABINET125_{}_{}'.format(cabinet_id, step.split('_')[2])}])
							self.data_dialog = 'CABINET125' + '|' + str(message_id) + '|' + step.split('_')[2] + '|' + str(task.task.id)
							self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, text=self.answer, parse_mode='HTML', message_id=message_id, reply_markup=self.keyboard)

						elif('CABINET125' in step):
							self.delete_dialog = True
							role = step.split('_')[2]
							task.task_finish(role)
							self.answer = font('bold', 'Поздравляем!🎉🎉🎉\nВы успешно закончили свой заказ!\n')
							self.answer += 'Мы рады, что вы обратились именно к нам!'
							self.answer += font('light', ' Если у вас есть предложения или идеи, как улучшить сервис, пишите @Viktor_Rachuk')
							self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, text=self.answer, parse_mode='HTML', message_id=message_id)
				else:
					task.task_list()
					if(task.keyboard.keyboard):
						text = 'Выберите задачу'
						self.telegram_bot.send_message(chat_id=self.client.chat_id, text=text, parse_mode='HTML', reply_markup=task.keyboard)
					else:
						text = 'Задач в разработке не найдено'
						self.telegram_bot.send_message(chat_id=self.client.chat_id, text=text, parse_mode='HTML')


	def pending_response(self, message):
		if('USER' in self.dialog.data):
			step = self.dialog.data.split('|')[0]
			message_id = self.dialog.data.split('|')[1]
			if(step == 'USER100'):
				if(not self.len_string(message, 50)):
					self.telegram_bot.send_message(chat_id=self.client.chat_id, text=self.answer, parse_mode='HTML', reply_markup=self.keyboard_cancel)
					return

				self.client.name = message
				self.client.save(update_fields=['name'])

			elif(step == 'USER101'):
				if(not self.len_string(message, 50)):
					self.telegram_bot.send_message(chat_id=self.client.chat_id, text=self.answer, parse_mode='HTML', reply_markup=self.keyboard_cancel)
					return

				self.client.city = message
				self.client.save(update_fields=['city'])

			elif(step == 'USER102'):
				if(not self.len_string(message, 255)):
					self.telegram_bot.send_message(chat_id=self.client.chat_id, text=self.answer, parse_mode='HTML', reply_markup=self.keyboard_cancel)
					return

				self.client.more = message
				self.client.save(update_fields=['more'])

			elif(step == 'USER103'):
				if(not self.len_string(message, 255)):
					self.telegram_bot.send_message(chat_id=self.client.chat_id, text=self.answer, parse_mode='HTML', reply_markup=self.keyboard_cancel)
					return

				self.client.withdraw = message
				self.client.save(update_fields=['withdraw'])

			self.user.card_raiting()
			self.answer = '{}\nИмя: {}\nСтрана: {}\nПодробнее обо мне: {}\nКуда выводить ср-ва: {}\n💎Рейтинг: {} ({})\n🏆Выполнено работ: {}\n'.format(
							font('bold', '🔥Ваша карточка 🔥'),
							font('bold', 'Не указано' if not self.client.name else self.client.name),
							font('bold', 'Не указано' if not self.client.city else self.client.city),
							font('bold', 'Не указано' if not self.client.more else self.client.more),
							font('bold', 'Не указано' if not self.client.withdraw else self.client.withdraw),
							font('bold', self.user.star),
							font('bold', self.user.assessment),
							font('bold', self.user.count_work)
						)

			self.answer += font('light', 'Для изменения информации нажимайте на кнопки\nНажмите {}, чтобы сохранить изменение'.format(font('bold', '«‎Применить»')))

			# telegram_bot.edit_message_reply_markup(chat_id=self.client.chat_id, message_id=self.dialog.data, parse_mode="HTML", text=self.answer)
			buttons = []
			keyboard = types.InlineKeyboardMarkup(True)
			buttons.append({'text': 'Применить', 'callback_data': 'USER777'})
			keyboard.keyboard = constructor(buttons, self.COUNT_ROW)

			self.telegram_bot.delete_message(chat_id=self.client.chat_id, message_id=message_id)
			# self.telegram_bot.edit_message_text(chat_id=self.client.chat_id, message_id=message_id, parse_mode="HTML", text=self.answer, reply_markup=keyboard)
			mes = self.telegram_bot.send_message(chat_id=self.client.chat_id, parse_mode="HTML", text=self.answer, reply_markup=keyboard)
			self.data_dialog = step + '|' + str(mes.message_id)
			self.delete_dialog = True
		
		elif('BALANCE' in self.dialog.data):
			step = self.dialog.data.split('|')[0]
			message_id = self.dialog.data.split('|')[1]

			if(not self.isfloat(message)):
				self.answer = 'Введите число'
				self.telegram_bot.send_message(chat_id=self.client.chat_id, text=self.answer, parse_mode='HTML', reply_markup=self.keyboard_cancel)
				return

			if(step == 'BALANCE100'):
				if(not self.between(message, 10, 5000)):
					self.telegram_bot.send_message(chat_id=self.client.chat_id, text=self.answer, parse_mode='HTML', reply_markup=self.keyboard_cancel)
					return

				self.delete_dialog = True
				self.user.take_pay(message)
				# self.answer = 'Ваша ссылка для оплаты готова (учитывается сервисный сбор платежной системы), нажмите <a href="#">Оплатить</a> и вы будете перенаправлены на сайт платежной системы.\n'.format(self.user.order.token)
				self.answer = 'Ваша ссылка для оплаты готова, нажмите <a href="#">Оплатить</a> и вы будете перенаправлены на сайт платежной системы.\n'.format(self.user.order.token)
				self.answer += font('light', 'Как правило, после оплаты деньги поступают на счет в течение минуты.')

			elif(step == 'BALANCE101'):
				if(not self.between(message, 100, 10000)):
					self.telegram_bot.send_message(chat_id=self.client.chat_id, text=self.answer, parse_mode='HTML', reply_markup=self.keyboard_cancel)
					return

				if(self.client.balance < float(message)):
					self.answer = 'Недостаточно средств'
					self.telegram_bot.send_message(chat_id=self.client.chat_id, text=self.answer, parse_mode='HTML', reply_markup=self.keyboard_cancel)
					return

				self.delete_dialog = True
				self.user.give_pay(message)
				self.answer = 'Заявка на вывод: №{} создана\nЗаявка будет обработана в течение 2-ух дней\nОжидание вывода: {} грн'.format(self.user.order.id, message if message else '0')
				self.telegram_bot.delete_message(chat_id=self.client.chat_id, message_id=message_id)

			elif(step == 'BALANCE121'):
				if(not self.len_string(message, 100)):
					self.telegram_bot.send_message(chat_id=self.client.chat_id, text=self.answer, parse_mode='HTML', reply_markup=self.keyboard_cancel)
					return

				self.delete_dialog = True
				if(not self.client.refer):
					self.user.referal(message)
					self.telegram_bot.delete_message(chat_id=self.client.chat_id, message_id=message_id)
					self.telegram_bot.send_message(chat_id=self.client.chat_id, text=self.user.answer)
				else:
					self.answer = 'Вы уже зарегистрированы за рефералом'
					self.telegram_bot.send_message(chat_id=self.client.chat_id, parse_mode='HTML', text=self.answer)

				return
			self.telegram_bot.send_message(chat_id=self.client.chat_id, parse_mode="HTML", text=self.answer, disable_web_page_preview=True)

		elif('CUSTOMER' in self.dialog.data):
			step = self.dialog.data.split('|')[0]
			message_id = self.dialog.data.split('|')[1]
			if('CUSTOMER120'  in self.dialog.data):
				if(not self.len_string(message, 200)):
					self.telegram_bot.send_message(chat_id=self.client.chat_id, text=self.answer, parse_mode='HTML', reply_markup=self.keyboard_cancel)
					return

				task = TaskClass(self.client)
				task.update_task(action='description', message=message)
				self.callback_response({'step': 'CUSTOMER130____', 'message_id': message_id}, 'inside')
				self.delete_dialog = True

			elif('CUSTOMERSEARCH120' in self.dialog.data):
				step = self.dialog.data.split('|')[0]
				message_id = self.dialog.data.split('|')[1]
				id_task = self.dialog.data.split('|')[2]

				task = TaskClass(self.client, 'CUSTOMERSEARCH', id_task)
				task.update_task(action='description', message=message)
				self.callback_response({'step': 'CUSTOMERSEARCH110_' + id_task, 'message_id': message_id}, 'inside')
				self.delete_dialog = True

			elif('CUSTOMER200' in self.dialog.data):
				step = self.dialog.data.split('|')[0]
				message_id = self.dialog.data.split('|')[1]
				id_feedback = self.dialog.data.split('|')[2]
				sender = self.dialog.data.split('|')[3]

				self.keyboard = types.InlineKeyboardMarkup(True)
				task = TaskClass(self.client, 'CUSTOMERSEARCH')
				if(sender == 'customer'): task.create_message(id_feedback, 'executor', message)
				elif(sender == 'executor'): task.create_message(id_feedback, 'customer', message)
				self.telegram_bot.delete_message(chat_id=self.client.chat_id, message_id=message_id)
				mes = self.telegram_bot.send_message(chat_id=self.client.chat_id, parse_mode="HTML", text=task.answer, reply_markup=task.keyboard)
				self.data_dialog = 'CUSTOMER200' + '|' + str(mes.message_id) + '|' + id_feedback + '|' + sender
				self.delete_dialog = True

		elif('EXECUTOR120' in self.dialog.data):
			step = self.dialog.data.split('|')[0]
			message_id = self.dialog.data.split('|')[1]
			id_task = self.dialog.data.split('|')[2]

			if(not self.isfloat(message)):
				self.answer = 'Введите число'
				self.telegram_bot.send_message(chat_id=self.client.chat_id, text=self.answer, parse_mode='HTML', reply_markup=self.keyboard_cancel)
				return

			if(not self.between(message, 10, 10000)):
				self.telegram_bot.send_message(chat_id=self.client.chat_id, text=self.answer, parse_mode='HTML', reply_markup=self.keyboard_cancel)
				return

			if('search' in self.dialog.data): search = True
			else: search = False
			task = TaskClass(self.client, 'CUSTOMERSEARCH', id_task)
			task.update_feedback(action='create+price', message=message)
			self.callback_response({'step': 'EXECUTOR130_' + id_task + search_list[search]['postfix'], 'message_id': message_id}, 'inside')

		elif('EXECUTOR130' in self.dialog.data):
			step = self.dialog.data.split('|')[0]
			message_id = self.dialog.data.split('|')[1]
			id_task = self.dialog.data.split('|')[2]

			if(not self.len_string(message, 200)):
				self.telegram_bot.send_message(chat_id=self.client.chat_id, text=self.answer, parse_mode='HTML', reply_markup=self.keyboard_cancel)
				return

			task = TaskClass(self.client, 'CUSTOMERSEARCH', id_task)
			if('search' in self.dialog.data): search = True
			else: search = False

			task.update_feedback(action='question', message=message, search=search)
			self.delete_dialog = True
			self.telegram_bot.delete_message(chat_id=self.client.chat_id, message_id=message_id)
			self.telegram_bot.send_message(chat_id=self.client.chat_id, parse_mode="HTML", text=task.answer, reply_markup=task.keyboard)

		elif('CABINET125' in self.dialog.data):
			message_id = self.dialog.data.split('|')[1]
			role = self.dialog.data.split('|')[2]
			id_task = self.dialog.data.split('|')[3]
			if(not self.len_string(message, 500)):
				self.telegram_bot.send_message(chat_id=self.client.chat_id, text=self.answer, parse_mode='HTML', reply_markup=self.keyboard_cancel)
				return
			
			task = TaskClass(self.client, 'CABINET')
			if(int(id_task) != task.task.id):
				self.answer = 'Перейдите в кабинет с задачей №{}'.format(id_task)
				self.telegram_bot.send_message(chat_id=self.client.chat_id, text=self.answer, parse_mode='HTML')
				return

			task.task_review(message=message, role=role)
			self.delete_dialog = True
			self.callback_response({'step': 'CABINET125_' + str(task.cabinet.id) + '_' + role, 'message_id': message_id}, 'inside')
		

	def file_response(self, data, type_file):
		if(self.telegram_bot.get_me().username == 'Shpargalochka_bot'):
			if(self.dialog.data):
				if(type_file == 'photo'):
					file_info = self.telegram_bot.get_file(data.photo[-1].file_id)
					file_name = file_info.file_path.split('/')[1]
				else:
					file_info = self.telegram_bot.get_file(data.document.file_id)
					file_name = data.document.file_name

				print(self.dialog.data)
				message_id = self.dialog.data.split('|')[1]
				downloaded_file = self.telegram_bot.download_file(file_info.file_path)
				if('CUSTOMERSEARCH130' in self.dialog.data):
					id_task = self.dialog.data.split('|')[2]
					task = TaskClass(self.client, 'CUSTOMERSEARCH', id_task)
					if('first' in self.dialog.data):
						task.task.files.clear()
						task.task.save()
						self.dialog.data = self.dialog.data.replace('|first', '')
						self.dialog.save(update_fields=['data'])
				elif('CUSTOMER130' in self.dialog.data):
					task = TaskClass(self.client, 'CUSTOMERCREATE')
				task.update_task(action='files', message=downloaded_file, file_name=file_name)
				self.telegram_bot.send_message(chat_id=self.client.chat_id, parse_mode="HTML", text=task.answer, reply_markup=task.keyboard)
		elif(self.telegram_bot.get_me().username == 'ShpargalochkaCab_bot'):
			task = TaskClass(self.client, 'CABINET')
			if(task.task):
				self.user.role_task()
				if(self.user.role == 'customer'): cabinet = Cabinet.objects.filter(task=task.task, role='executor')
				elif(self.user.role == 'executor'): cabinet = Cabinet.objects.filter(task=task.task, role='customer')

				if(type_file == 'photo'):
					file_info = self.telegram_bot.get_file(data.photo[-1].file_id)
					file_name = file_info.file_path.split('/')[1]
				else:
					file_info = self.telegram_bot.get_file(data.document.file_id)
					file_name = data.document.file_name

				print(file_info.file_path)
				downloaded_file = self.telegram_bot.download_file(file_info.file_path)
				with open("#" + file_name, "wb") as f:
					f.write(downloaded_file)
				reopen = open("#" + file_name, "rb")
				django_file = File(reopen)
				file = Files.objects.create(upload=django_file)
				cabinet_i = Cabinet.objects.filter(task=task.task, client=self.client)
				
				if(not cabinet[0].active):
					Cabinetmessage.objects.create(cabinet_record=cabinet_i[0], file=file, state=True)
					from astudy.settings import ASTUDY_TOKEN
					astudy = telebot.TeleBot(ASTUDY_TOKEN)
					answer = '🔔 У Вас новое сообщение по заказу {}\n'.format(font('bold', '#{} {}'.format(cabinet[0].task.id, cabinet[0].task.subject.name)))
					answer += font('light', 'Перейдите в ') + font('bold', '«Кабинет» ') + font('light', 'и прочитайте его')
					keyboard = types.InlineKeyboardMarkup(True)
					keyboard.keyboard.append([{'text': 'Кабинет', 'url': '#'}])
					astudy.send_message(chat_id=cabinet[0].client.chat_id, text=answer, parse_mode='HTML', reply_markup=keyboard)
				else:
					if(type_file == 'photo'):
						self.telegram_bot.send_photo(chat_id=cabinet[0].client.chat_id, photo=data.photo[-1].file_id)
					else:
						self.telegram_bot.send_document(cabinet[0].client.chat_id, data.document.file_id)

					Cabinetmessage.objects.create(cabinet_record=cabinet_i[0], file=file)

				os.remove("#" + file_name)

			else:
				task.task_list()
				if(task.keyboard.keyboard):
					text = 'Выберите задачу'
					self.telegram_bot.send_message(chat_id=self.client.chat_id, text=text, parse_mode='HTML', reply_markup=task.keyboard)
				else:
					text = 'Задач в разработке не найдено'
					self.telegram_bot.send_message(chat_id=self.client.chat_id, text=text, parse_mode='HTML')