# -*- coding: utf-8 -*-
import datetime
import math
from bot.models import *
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from liqpay.liqpay import LiqPay
from bot.classes.pay import *
from django.db.models import Count, Min, Sum, Avg
import uuid

class User:

	def __init__(self, chat_id, bot):
		self.client = Clients.objects.filter(chat_id=chat_id)
		if(self.client):
			self.client = self.client[0]
			dialog = DialogControll.objects.filter(client=self.client, bot=bot)
			if(dialog):
				self.dialog = dialog[0]
			else:
				self.dialog = None
		else:
			self.client = Clients.objects.create(chat_id=chat_id, refer_code=uuid.uuid4())
			self.dialog = None

		self.commissions = Commissions.objects.filter()[0]
	def create_dialog(self, data, bot):
		self.dialog = DialogControll.objects.create(client=self.client, data=data, bot=bot)

	def delete_dialog(self):
		if(self.dialog):
			self.dialog.delete()
			self.dialog = None

	def take_pay(self, message):
		self.order = Payliq.objects.create(client=self.client, amount_one=float(message), amount_two=math.ceil(float(message) / self.commissions.amount_one))
		pay = Pay()
		pay.create_pay(str(math.ceil(float(message) / self.commissions.amount_one)), str(self.order.id))
		self.order.token = pay.data
		self.order.save(update_fields=['token'])

	def give_pay(self, message):
		self.client.balance -= math.floor(float(message) / self.commissions.amount_two)
		self.client.save(update_fields=['balance'])
		self.order = Withdrawal.objects.create(client=self.client, amount_one=math.floor(float(message)), amount_two=math.floor(float(message) / self.commissions.amount_two))

	def withdrawal_list(self):
		self.withdrawal_sum = Withdrawal.objects.filter(client=self.client, state=False).aggregate(Sum('amount_two'))

	def role_task(self):
		cabinet = Cabinet.objects.filter(client=self.client, active=True)
		if(cabinet): self.role = cabinet[0].role
		else: self.role = None

	def referal(self, code):
		refer = Clients.objects.filter(refer_code=code)
		if(refer):
			if(self.client.id != refer[0].id):
				refer = refer[0]
				self.client.refer = refer
				self.client.bonuse = True
				self.client.save(update_fields=['refer', 'bonuse'])
				self.answer = 'Код принят, вы получаете скидку {}% на первый заказ'.format(math.ceil((1 - self.commissions.amount_four) * 100))
			else:
				self.answer = 'Вы ввели свой код'
		else:
			self.answer = 'Пользователя с таким кодом не найдено'

	def raiting(self, subject, executor):
		assessment = Assessment.objects.filter(executor=executor).aggregate(Avg('grade'))
		self.count_work = Tasks.objects.filter(executor=executor, finish=True).count()
		if(not assessment['grade__avg']):
			raiting_one = 0
			raiting_two = 0
			self.assessment = 0
		else:
			raiting_one = round(int(assessment['grade__avg'] // 1), 1)
			raiting_two = round(assessment['grade__avg'] % 1, 2)
			self.assessment = round(assessment['grade__avg'], 1)

		self.star = ''
		for x in range(raiting_one): self.star += '⭐️'
		if(raiting_two != 0): self.star += '✨'

	def card_raiting(self):
		assessment = Assessment.objects.filter(executor=self.client).aggregate(Avg('grade'))
		self.count_work = Tasks.objects.filter(executor=self.client, finish=True).count()
		if(not assessment['grade__avg']):
			raiting_one = 0
			raiting_two = 0
			self.assessment = 0
		else:
			raiting_one = round(int(assessment['grade__avg'] // 1), 1)
			raiting_two = round(assessment['grade__avg'] % 1, 2)
			self.assessment = round(assessment['grade__avg'], 1)

		print(assessment)
		self.star = ''
		for x in range(raiting_one): self.star += '⭐️'
		if(raiting_two != 0): self.star += '✨'
