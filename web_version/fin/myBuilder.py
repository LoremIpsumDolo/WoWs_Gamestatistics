import json
import sqlite3


def open_config():
	with open('fin/config.json') as conf:
		conf = json.load(conf)
		return conf


conf = open_config()
Gamefile = conf.get('game_path')
database_path = conf.get('database_path')
application_id = str(conf.get('application_id'))


def get_unique_dates():
	conn = sqlite3.connect(database_path)
	c = conn.cursor()
	Return = []
	c.execute("""
		SELECT DISTINCT
			battle_timestamp
		FROM
			tbl_player
		""")
	for row in c.fetchall():
		Return.append(row[0])
	return (Return)


def get_names_for_date(battle_timestamp):
	conn = sqlite3.connect(database_path)
	c = conn.cursor()
	Return = []
	c.execute("""
		SELECT DISTINCT
			name
		FROM
			tbl_player
		WHERE
			battle_timestamp=:battle_timestamp
		""", {'battle_timestamp': battle_timestamp}
	          )
	for row in c.fetchall():
		Return.append(row[0])
	return (Return)


def print_full_results(battle_timestamp, relation, ship_type_long):
	conn = sqlite3.connect(database_path)
	c = conn.cursor()
	c.execute("""
		SELECT
			name,
			ship_name,
			type,
			TotalAvg,
			TotalBattles,
			ShipAvg,
			BattlesShip,
			relation,
			radar
		FROM
			tbl_player
		INNER JOIN
			tbl_ships
		ON
			tbl_ships.ship_id = tbl_player.shipId
		INNER JOIN
			tbl_player_stats
		ON
			tbl_player_stats.PStat_id = tbl_player.id
		WHERE
			battle_timestamp=:battle_timestamp
		AND
			relation=:relation
		AND
			tbl_ships.type=:ship_type_long
		""", {'battle_timestamp': battle_timestamp, 'relation': relation, 'ship_type_long': ship_type_long}
	          )
	return (c.fetchall())


def print_full_Bot_results(battle_timestamp, relation, ship_type_long):
	conn = sqlite3.connect(database_path)
	c = conn.cursor()
	c.execute("""
		SELECT
			name,
			ship_name,			
			type,
			relation,
			radar
		FROM
			tbl_player
		INNER JOIN
			tbl_ships
		ON
			tbl_ships.ship_id = tbl_player.shipId
		WHERE
			battle_timestamp=:battle_timestamp
		AND
			relation=:relation
		AND
			tbl_ships.type=:ship_type_long
		AND
			bot='1'
		""", {'battle_timestamp': battle_timestamp, 'relation': relation, 'ship_type_long': ship_type_long}
	          )
	resB = c.fetchall()
	return (resB)


def merge_lists(resultA, resultB):
	Rows = []

	for x in range(len(resultA)):
		if str(resultA[x][3]) <= resultB[x][3]:
			avgA = 'red wr'
			avgB = 'green wr'
		else:
			avgA = 'green wr'
			avgB = 'red wr'

		if str(resultA[x][8]) == '1':
			radarA = 'radar'
		else:
			radarA = 'noradar'

		if str(resultB[x][8]) == '1':
			radarB = 'radar'
		else:
			radarB = 'noradar'

		row = {
			'playerA_name': resultA[x][0],
			'playerB_name': resultB[x][0],
			'playerA_ship_name': resultA[x][1],
			'playerB_ship_name': resultB[x][1],

			'playerA_type': str(resultA[x][2] + '.png'),
			'playerB_type': str(resultB[x][2] + '.png'),
			'radarA': radarA,
			'radarB': radarB,

			'playerA_avg': resultA[x][3],
			'playerB_avg': resultB[x][3],
			'playerA_TotalBattles': resultA[x][4],
			'playerB_TotalBattles': resultB[x][4],
			'playerA_ShipAvg': resultA[x][5],
			'playerB_ShipAvg': resultB[x][5],
			'playerA_ShipBattles': resultA[x][6],
			'playerB_ShipBattles': resultB[x][6],
			'playerA_avgClass': avgA,
			'playerB_avgClass': avgB
		}
		Rows.append(row)
	return (Rows)


def Getdatabase_pathdata(battle_timestamp):
	resultA = []
	resultB = []
	Team = ('1', '2')
	Type = ('AirCarrier', 'Battleship', 'Cruiser', 'Destroyer')

	for team in Team:
		for stype in Type:
			_result = print_full_results(battle_timestamp, team, stype)
			for res in _result:

				if team == '1':
					resultA.append(res)
				elif team == '2':
					resultB.append(res)

	MergedList = merge_lists(resultA, resultB)
	return (MergedList)


# def build_export(LocalDate):
# 	battle_timestamp = LocalDate
# 	Export = [
# 		{
# 			'date': battle_timestamp
# 		},
# 		Getdatabase_pathdata(battle_timestamp)
# 	]
# 	return (Export)


def build_export(LocalDate):
	battle_timestamp = LocalDate
	Export = [
		{
			'date': battle_timestamp
		},
		{
			'data': Getdatabase_pathdata(battle_timestamp)
		}]

	return (Export)


# LocalDate = '25.11.2020 16:25:55'
# exportData = build_export(LocalDate)

# print(exportData[1]['data'])


#
# print(exportData[0]['date'])
#

# (exportData)
# for field in exportData:
# 	for row in field:
# 		print(row)
