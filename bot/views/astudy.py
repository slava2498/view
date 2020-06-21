from django.shortcuts import render
from django.http import HttpResponse
import telebot
from telebot import TeleBot, types
import json
import time
import random
import sqlite3
from django.views.decorators.csrf import csrf_exempt
from bot.classes.user import *
from bot.classes.stairs import *
from bot.classes.pay import *
import django.db
from astudy.settings import ASTUDY_TOKEN as TOKEN

telegrambot = telebot.TeleBot(TOKEN)

@csrf_exempt
def webhook(request):
	if request.method == 'POST':
		json_str = request.body.decode('UTF-8')
		update = types.Update.de_json(json_str)
		telegrambot.process_new_updates([update])
		return HttpResponse(status=200)
	return HttpResponse(status=403)

@csrf_exempt
def pay(request):
	if request.method == 'POST':
		pay = Pay()
		pay.processing_pay(request.POST)
		telegrambot.send_message(chat_id=pay.client.chat_id, text=pay.data, parse_mode='HTML')
		return HttpResponse(status=200)
	return HttpResponse(status=403)
	
@telegrambot.message_handler(content_types=['text'])
def main(message):
	user = User(message.chat.id, telegrambot.get_me().username)
	message = message.text
	stairs = Stairs(user, telegrambot)
	if(user.dialog):
		stairs.pending_response(message)
	else:
		stairs.quick_response(message.lower())

	print(36,stairs.data_dialog)
	if(stairs.delete_dialog):
		user.delete_dialog()

	if(stairs.data_dialog):
		user.create_dialog(stairs.data_dialog, telegrambot.get_me().username)

	django.db.close_old_connections()

@telegrambot.callback_query_handler(func=lambda call: True)
def text(call):
	user = User(call.message.chat.id, telegrambot.get_me().username)
	stairs = Stairs(user, telegrambot)
	stairs.callback_response(call)

	print(51,stairs.data_dialog)
	if(stairs.delete_dialog):
		user.delete_dialog()

	if(stairs.data_dialog):
		print(stairs.data_dialog)
		user.create_dialog(stairs.data_dialog, telegrambot.get_me().username)
		print(stairs.data_dialog)

	django.db.close_old_connections()

@telegrambot.message_handler(content_types=['document', 'photo'])
def handle_docs_photo(message):
	user = User(message.chat.id, telegrambot.get_me().username)
	stairs = Stairs(user, telegrambot)
	stairs.file_response(message, message.content_type)

	print(51,stairs.data_dialog)
	if(stairs.delete_dialog):
		user.delete_dialog()

	if(stairs.data_dialog):
		print(stairs.data_dialog)
		user.create_dialog(stairs.data_dialog, telegrambot.get_me().username)
		print(stairs.data_dialog)

	django.db.close_old_connections()