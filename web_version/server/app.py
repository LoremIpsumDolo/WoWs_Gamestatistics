import json

from flask import Flask, request, json, jsonify, url_for, render_template

app = Flask(__name__)


def save_as_json(data):
	with open('result.json', 'w') as outfile:
		json.dump(data, outfile, ensure_ascii=False)


def open_timestamp_from_file():
	try:
		with open('result.json') as Log:
			LogJSON = json.load(Log)
			LatestTimestamp = LogJSON[0]["date"]
			Log.close()

			return (LatestTimestamp)
	except:
		LatestTimestamp = '22.10.2020 08:07:49'
		return (LatestTimestamp)


def open_data_from_file():
	try:
		with open('result.json') as Log:
			LogJSON = json.load(Log)
			Rows = LogJSON[1]['data']
			Log.close()
			return Rows
	except:
		return "404"


@app.route('/table.html')
def table():
	Rows = open_data_from_file()
	image_file = url_for('static', filename='/' + 'static' + 'playerA_type')
	return render_template('table.html', Rows=Rows, image_file=image_file)


@app.route('/')
def index():
	return render_template('index.html')


@app.route('/api', methods=['GET', 'POST'])
def return_all():
	if request.method == 'GET':
		try:
			Result = open_timestamp_from_file()
			print(Result)
			return jsonify(Result)
		except:
			return 'error'

	elif request.method == 'POST':
		req_data = request.get_json()
		save_as_json(req_data)
		return jsonify(req_data)


print(open_timestamp_from_file())

if __name__ == '__main__':
	app.run()
