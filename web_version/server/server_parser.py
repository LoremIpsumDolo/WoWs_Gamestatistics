import json


def save_as_json(data):
	with open('py/result.json', 'w') as outfile:
		#json.dump(data, outfile, ensure_ascii=False)
		json.dump(data, outfile)


def open_timestamp_from_file():
	try:
		with open('py/result.json') as Log:
			LogJSON = json.load(Log)
			LatestTimestamp = LogJSON[0]["date"]
			Log.close()

			return (LatestTimestamp)
	except:
		LatestTimestamp = '22.10.2020 08:07:49'
		return (LatestTimestamp)


def open_data_from_file():
	try:
		with open('py/result.json') as Log:
			LogJSON = json.load(Log)
			Rows = LogJSON[1]['data']
			Log.close()
			return Rows
	except:
		return "404"