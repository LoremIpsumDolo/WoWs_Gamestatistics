import os
import json
import requests
from fin import myBuilder, myParser
import time


def open_config():
	if os.path.isfile('fin/config.json') != True:
		return ('no config found')
	else:
		print('config found')

	with open('fin/config.json') as conf:
		conf = json.load(conf)
		return conf


conf = open_config()
logfile = conf.get('game_path')
database_path = conf.get('database_path')
application_id = str(conf.get('application_id'))
url = str(conf.get('url'))


def get_local_date():
	try:
		with open(logfile) as Log:
			LogJSON = json.load(Log)
			Log.close()
			LocalDateTime = LogJSON['dateTime']
			print('LocalDateTime:', LocalDateTime)
			return LocalDateTime
	except:
		print('no logfile found')


def get_remote_date():
	try:
		r = requests.get(url)
		answer = r.json()
		if answer is not None:
			print('RemoteDate:', answer)
			return answer
		else:
			print('no remote date found')
	except:
		print('no remote connection found')


def build_exportData(LocalDate):
	print('exportData:')
	exportData = myBuilder.build_export(LocalDate)
	return (exportData)


def post_Result(Result):
	try:
		res = requests.post(url, json=Result)
		if res.ok:
			print(res.json())
	except:
		print('error POST request')


def compare_dates():
	RemoteDate = str(get_remote_date())
	LocalDate = str(get_local_date())

	if LocalDate == RemoteDate:
		print('dates match')
	else:
		print('no match')
		print('LocalDate:', LocalDate)
		print('RemoteDate:', RemoteDate)

		try:
			print(myParser.main_update())
			Result = build_exportData(LocalDate)
			post_Result(Result)
			time.sleep(10)
		except:
			print('error parsing')


def loop():
	while True:
		compare_dates()
		time.sleep(5)


# def main():

loop()
