import json
import sqlite3
import requests

URL_a = 'https://api.worldofwarships.eu/wows/account/list/?'
URL_e = 'https://api.worldofwarships.eu/wows/encyclopedia/ships/?'
URL_es = 'https://api.worldofwarships.eu/wows/account/info/?'
URL_PS = 'https://api.worldofwarships.eu/wows/ships/stats/?'


def open_config():
	with open('fin/config.json') as conf:
		conf = json.load(conf)
		return conf


conf = open_config()
Gamefile = conf.get('game_path')
database_path = conf.get('database_path')
application_id = str(conf.get('application_id'))


####################################
#     main_update	 start         #
####################################


def open_log():
	with open(Gamefile) as f:
		logfile = json.load(f)
		return (logfile)


def update_player_tbl(battle_timestamp, player_relation, player, bot):
	conn = sqlite3.connect(database_path)
	c = conn.cursor()
	c.execute("""
		INSERT OR IGNORE INTO
			tbl_player
		VALUES (
			:id,
			:battle_timestamp,
			:shipId,
			:relation,
			:player_id,
			:name,
			:bot )
			""", {
		'id': None,
		'battle_timestamp': battle_timestamp,
		'shipId': player['shipId'],
		'relation': player_relation,
		'player_id': player['id'],
		'name': player['name'],
		'bot': bot
	})
	conn.commit()


def update_bot_db(battle_timestamp):
	def bot_PStatId(battle_timestamp):
		# print(battle_timestamp, player)
		conn = sqlite3.connect(database_path)
		c = conn.cursor()
		c.execute("""
		SELECT
			id,
			name
		FROM
			tbl_player
		WHERE
			battle_timestamp=:battle_timestamp
		AND
			bot='1'
		""", {
			'battle_timestamp': battle_timestamp
		})
		ReturnID = c.fetchall()
		return (ReturnID)

	PStat_id = bot_PStatId(battle_timestamp)
	for row in PStat_id:
		conn = sqlite3.connect(database_path)
		c = conn.cursor()
		c.execute("""
			INSERT OR IGNORE INTO
				tbl_player_stats
			VALUES (
				:PStat_id,
				:account_id,
				:TotalBattles,
				:TotalWins,
				:TotalAvg,
				:ShipWins,
				:BattlesShip,
				:ShipAvg )
				""", {
			'PStat_id': row[0],
			'nickname': row[1],
			'battle_timestamp': battle_timestamp,
			'account_id': '0',
			'TotalBattles': '0',
			'TotalWins': '0',
			'TotalAvg': '0',
			'ShipWins': '0',
			'BattlesShip': '0',
			'ShipAvg': '0',
		})
		conn.commit()


def update_player_db():
	print('update_player_db')
	log = open_log()
	battle_timestamp = log['dateTime']

	for player in log['vehicles']:

		player_name = player['name']
		rel = player['relation']

		if player_name.startswith(':'):
			Bot = '1'
		else:
			Bot = '0'

		if rel == 0:
			player_relation = '1'
		elif rel == 1:
			player_relation = '1'
		elif rel == 2:
			player_relation = '2'

		update_player_tbl(battle_timestamp, player_relation, player, Bot)

	update_bot_db(battle_timestamp)


####################################
#     main_update	 end           #
####################################

####################################
#     get_PVP_stats	 start         #
####################################


def select_ship_for_player(nickname, battle_timestamp):
	conn = sqlite3.connect(database_path)
	c = conn.cursor()
	c.execute("""
		SELECT
			shipId
		FROM
			tbl_player
		WHERE
			name=:nickname
		AND
			battle_timestamp=:battle_timestamp
		AND
			bot='0'
			""", {'nickname': nickname, 'battle_timestamp': battle_timestamp}
	          )
	shipId = c.fetchall()
	return (shipId[0][0])


def get_all_stats(all_player_stats, battle_timestamp):
	print('get_all_stats')
	PvP_stat_list = []
	battle_timestamp = battle_timestamp
	null = None

	def request_shipstats(id, nickname):
		nickname = str(nickname)
		account_id = str(id)
		shipId = str(select_ship_for_player(nickname, battle_timestamp))

		ShipURL = (
				URL_PS + application_id + '&account_id=' + account_id + '&fields=pvp.battles%2C+pvp.wins&ship_id=' + shipId)
		r = requests.get(ShipURL)
		PlayerShipStats = json.loads(r.text)

		if PlayerShipStats['meta']['count'] != 0 and PlayerShipStats['data'] is not None:
			wins_ship = PlayerShipStats['data'][account_id][0]['pvp']['wins']
			battles_ship = PlayerShipStats['data'][account_id][0]['pvp']['battles']
			avg_ship_t = wins_ship / battles_ship * 100
			avg_ship = ("{:.2f}".format(avg_ship_t) + '%')
		else:
			wins_ship = '0'
			battles_ship = '0'
			avg_ship = '0'

		stats = {
			'battle_timestamp': battle_timestamp,
			'nickname': nickname,
			'account_id': account_id,
			'shipId': shipId,
			'wins_ship': wins_ship,
			'battles_ship': battles_ship,
			'avg_ship': avg_ship,
		}
		return (stats)

	for stat in all_player_stats['data']:
		id = stat
		nickname = all_player_stats['data'][id]['nickname']

		PlayerShipStats = request_shipstats(id, nickname)

		statistics = all_player_stats['data'][id]['statistics']
		if statistics is not None:
			status = 'public'
			pvp = statistics['pvp']
			TotalBattles = pvp['battles']
			TotalWins = pvp['wins']
			_TotalAvg = TotalWins / TotalBattles * 100
			TotalAvg = ("{:.2f}".format(_TotalAvg) + '%')

			ShipWins = PlayerShipStats['wins_ship']
			BattlesShip = PlayerShipStats['battles_ship']
			ShipAvg = PlayerShipStats['avg_ship']

		elif statistics is None or statistics == 'null':
			status = 'private'
			TotalBattles = '0'
			TotalWins = '0'
			TotalAvg = '0'
			ShipWins = '0'
			BattlesShip = '0'
			ShipAvg = '0'

		PlayerList = {
			'status': status,
			'battle_timestamp': battle_timestamp,
			'account_id': id,
			'nickname': nickname,
			'TotalBattles': TotalBattles,
			'TotalWins': TotalWins,
			'TotalAvg': TotalAvg,
			'ShipWins': ShipWins,
			'BattlesShip': BattlesShip,
			'ShipAvg': ShipAvg
		}
		PvP_stat_list.append(PlayerList)
	return (PvP_stat_list)


def get_latest_ts():
	conn = sqlite3.connect(database_path)
	c = conn.cursor()
	c.execute("SELECT DISTINCT battle_timestamp FROM tbl_player ORDER BY id DESC LIMIT 1")
	latest_ts = c.fetchall()
	return (latest_ts[0][0])


def player_tbl_select_all_by_team(battle_timestamp):
	conn = sqlite3.connect(database_path)
	c = conn.cursor()
	c.execute("""
		SELECT
			name
		FROM
			tbl_player
		WHERE
			battle_timestamp=:battle_timestamp
		AND
			bot='0'
			""", {'battle_timestamp': battle_timestamp}
	          )
	return_r = []
	for r in c.fetchall():
		return_r.append(r[0])
	return (return_r)


def get_PVP_stats():
	print('get_PVP_stats')
	battle_timestamp = str(get_latest_ts())

	def request_account_ids():
		print('request_account_ids')
		_PlayerName = player_tbl_select_all_by_team(battle_timestamp)
		joined_string = '%2C'.join(_PlayerName)
		r = requests.get(
			URL_a + application_id + '&fields=account_id%2C+nickname&search=' + joined_string + '&type=exact')
		account_id = json.loads(r.text)
		return (account_id)

	def request_all_playerstats(account_id_list):
		print('request_all_playerstats')
		joined_string = '%2C+'.join(account_id_list)
		r = requests.get(
			URL_es + application_id + '&account_id=' + joined_string + '&fields=nickname%2C+statistics.pvp.battles%2C+statistics.pvp.wins')
		pvp_stats = json.loads(r.text)
		return (pvp_stats)

	def make_id_list(account_id):
		print('make_id_list')
		account_id_list = []
		for account in account_id['data']:
			account_id_list.append(str(account['account_id']))
		return (account_id_list)

	account_data = request_account_ids()
	account_id_list = make_id_list(account_data)
	all_player_stats = request_all_playerstats(account_id_list)

	PvPStats = get_all_stats(all_player_stats, battle_timestamp)
	return (PvPStats)


####################################
#     get_PVP_stats	 end           #
####################################

####################################
#     update_stats_tbl	 start     #
####################################


def update_stats_tbl(PvPStats):
	def player_PStatId(nickname, battle_timestamp):
		conn = sqlite3.connect(database_path)
		c = conn.cursor()
		c.execute("""
		SELECT
			id
		FROM
			tbl_player
		WHERE
			battle_timestamp=:battle_timestamp
		AND
			name=:nickname
		""", {
			'nickname': nickname,
			'battle_timestamp': battle_timestamp
		})
		ReturnID = c.fetchall()
		return (ReturnID[0][0])

	for player in PvPStats:
		PStat_id = player_PStatId(player['nickname'], player['battle_timestamp'])

		conn = sqlite3.connect(database_path)
		c = conn.cursor()
		c.execute("""
			INSERT OR IGNORE INTO
				tbl_player_stats
			VALUES (
				:PStat_id,
				:account_id,
				:TotalBattles,
				:TotalWins,
				:TotalAvg,
				:ShipWins,
				:BattlesShip,
				:ShipAvg )
				""", {
			'PStat_id': PStat_id,
			'nickname': player['nickname'],
			'battle_timestamp': player['battle_timestamp'],
			'account_id': player['account_id'],
			'TotalBattles': player['TotalBattles'],
			'TotalWins': player['TotalWins'],
			'TotalAvg': player['TotalAvg'],
			'ShipWins': player['ShipWins'],
			'BattlesShip': player['BattlesShip'],
			'ShipAvg': player['ShipAvg']
		})
		conn.commit()





def main_update():
	update_player_db()
	PvPStats = get_PVP_stats()
	update_stats_tbl(PvPStats)
	return PvPStats



# main_update()


# def cleanup():
#	player_tbl_drop()
#	make_tbl_player()
#	make_tbl_player_stats()
#	update_player_db()
#	for player in player_tbl_select_all():
#		print(player)
