# -*- coding: utf-8 -*-
import datetime
import base64
import json
from bot.models import *
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from liqpay.liqpay import LiqPay
from astudy.settings import font

class Pay:

	def __init__(self):
		self.liqpay = LiqPay('#', '#')
		self.data = ''

	def font(self, type_font, message):
		font_array = {'bold': '<b>' + str(message) + '</b>', 'light': '<i>' + str(message) + '</i>'}
		return font_array[type_font]

	def create_pay(self, message, order_id):
		res = self.liqpay.api("request", {
			"action"    : "invoice_bot",
			"version"   : "3",
			"amount"    : message,
			"currency"  : "UAH",
			"order_id"  : order_id,
			"phone"  : "#",
			"server_url": '#'
		})
		
		self.data = res['token']

	def processing_pay(self, json_data):
		data = base64.b64decode(json_data['data']).decode('utf-8')

		sign = self.liqpay.str_to_sign(
			'#' +
			json_data['data'] +
			'#'
		)

		json_string = json.loads(data)
		print(json_data['signature'])
		print(sign)
		if(json_data['signature'] == sign):
			transactions = Payliq.objects.filter(id=json_string['order_id'])[0]
			transactions.state = True
			transactions.save(update_fields=['state'])

			client = Clients.objects.filter(id=transactions.client.id)[0]
			client.balance += transactions.amount_one
			client.save(update_fields=['balance'])

			self.client = client
			self.data = '{}!\n🎈Ваш баланс пополнен на {}\n{}'.format(font('bold', 'Поздравляем'), font('bold', str(transactions.amount_one) + ' грн'), font('light', 'Переходите в {} и выбирайте желаемого помощника 👇'.format(font('bold', '«Мои заказы 📝»'))))

