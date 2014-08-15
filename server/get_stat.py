#!/usr/bin/python

import os
import sys
import datetime
import xlsxwriter
import shutil
from xlsxwriter.utility import xl_rowcol_to_cell

pwd = os.getcwd()

def move_re_log(file):
	if len(file) < 4 or file[-4:] != ".log":
		return
	name_part = file[:-4]

	if (not os.access("re", os.F_OK)):
		os.mkdir("re")

	shutil.move(name_part + ".log", "re")
	shutil.move(name_part + "_msg.log", "re")

def get_date_from_log(file):
	if len(file) != 27 or file[:4] != "log_" or file[-4:] != ".log":
		return False
	
	return datetime.datetime.strptime(file, "log_%Y-%m-%d-%H-%M-%S.log")

def get_name_value_pair(line, value_index, player_index = None, sentinel = None):
	line = line.split(' ')
	if player_index != None:
		try:
			player_index_end = line[player_index:].index(sentinel)
			name = ' '.join(line[player_index : player_index + player_index_end])
		except ValueError:
			name = None
	else:
		name = None
	value = line[value_index]
	return name, value	

def get_player_count(fin):
	fin.readline()
	fin.readline()
	fin.readline()
	line = fin.readline()
	return eval(line[line.rfind('=')+2:])

def readline(fin):
	ret = fin.readline().rstrip('\n')
	#print ret
	return ret

## returns the number of total games
def get_player_detailed_stats(fin, win_by_all_in, time):
	chips = {}
	win_by_all_in_single_game = {}
	current_bets = {}
	while True:
		line = readline(fin)
		if line.startswith("[Player "):
			line_list = line.split(' ')
			name = ' '.join(line_list[2:])
			chips[name] = 3000
			win_by_all_in_single_game[name] = 0
			current_bets[name] = 0
		elif line.startswith("[GAMES INFO]"):
			line_list = line.split(' ')
			initial_chips = eval(line_list[-1])
			for name in chips.viewkeys():
				chips[name] = initial_chips
			readline(fin)
			break
		elif line.startswith("[Exception]"):
			return -1
		else:
			print "unknown situation:", line
			sys.exit(1)

	while True:
		readline(fin)
		line = readline(fin)
		if line.startswith("[FINAL STAT]"):
			break

		## GAME INFO
		while True:
			line = readline(fin)
			if line.startswith("[GAME INFO]"):
				if line.find("blind bets") != -1:
					break
			elif line.startswith("[Exception]"):
				return -1
			else:
				break
		if not line.startswith("[GAME INFO]"):
			break

		## small blind
		name, value = get_name_value_pair(line, -1, 3, "blind")
		value = eval(value)
		chips[name] -= value
		current_bets[name] = value

		## big blind
		line = readline(fin)
		if line.startswith("[Exception]"):
			return -1
		name, value = get_name_value_pair(line, -1, 3, "blind")
		value = eval(value)
		chips[name] -= value
		current_bets[name] = value
	
		while True:
			line = readline(fin)
			if line.startswith("[PREFLOP]"):
				break
			elif line.startswith("[Exception]"):
				return -1
		for round_name in ("[PREFLOP]", "[FLOP]", "[TURN]", "[RIVER]"):
			if not line.startswith(round_name):
				break
			while True:
				line = readline(fin)
				if line.startswith("[WARNING]"):
					continue
				elif line.startswith("[Exception]"):
					return -1
				elif not line.startswith(round_name):
					break
				else:
					if line.find("calls") != -1:
						if len(current_bets.viewvalues()) == 0:
							to_bet = 0
						else:
							to_bet = max(current_bets.viewvalues())
						name, value = get_name_value_pair(line, -1, 2, "calls")
						to_bet -= current_bets[name]
						chips[name] -= to_bet
						current_bets[name] += to_bet
					elif line.find("raises by") != -1:
						if len(current_bets.viewvalues()) == 0:
							to_bet = 0
						else:
							to_bet = max(current_bets.viewvalues())
						name, value = get_name_value_pair(line, -1, 2, "raises")
						to_bet -= current_bets[name]
						value = eval(value)
						to_bet += value
						chips[name] -= to_bet
						current_bets[name] += to_bet
			for name in current_bets.viewkeys():
				current_bets[name] = 0
		
		## GAME STAT
		while not line.startswith("[GAME STAT]"):
			if line.startswith("[Exception]"):
				return -1
			line = readline(fin)

		while True:
			line = readline(fin)
			if line.startswith("[GAME STAT]"):
				if line.endswith("chips"):
					name, value = get_name_value_pair(line, -2, 3, "gets")
					value = eval(value)
					if chips[name] == 0:
						win_by_all_in_single_game[name] += 1
					chips[name] += value
			elif line == "":
				break
			elif line.startswith("[GAMES STAT]"):
				continue
			elif line.startswith("[Exception]"):
				return -1
			else:
				print "Unknown situation:", line
				sys.exit(1)

	if not line.startswith("[FINAL STAT]"):
		print "Unknown situation:", line
		sys.exit(1)

	total_games = eval(line[line.rfind(':')+2:])

	for name, value in win_by_all_in_single_game.viewitems():
		add_item(win_by_all_in, name, value, time)	

	return total_games

## Deprecated
def get_total_games(fin):
	line = fin.readline()
	while len(line) < 12 or line[:12] != "[FINAL STAT]":
		if len(line) >= 11 and line[:11] == "[Exception]":
			return -1
		line = fin.readline()
	return eval(line[line.rfind(':')+2:])

def get_original_name(name):
	p = name.rfind('_')
	if p != -1:
		p = name.rfind('_', 0, p)
	if p!= -1:
		return name[:p]
	else:
		return name

def add_item(stat_map, name, item, time):
	name = get_original_name(name)
	if name not in stat_map:
		stat_map[name] = {time : item}
	else:
		stat_map[name][time] = item

def get_stats_of_one_item(fin, stat_map, skip_cnt, player_cnt, value_index, player_index, sentinel, time, do_eval = True):
	while skip_cnt > 0:
		skip_cnt -= 1
		fin.readline()

	while player_cnt > 0:
		player_cnt -= 1
		line = fin.readline()
		name, value = get_name_value_pair(line, value_index, player_index, sentinel)
		if do_eval:
			value = eval(value)
		add_item(stat_map, name, value, time)

def get_time_order(Time):
	return sorted(range(len(Time)), lambda x, y : (Time[x] < Time[y] and -1) or 1)

def reorder_per_game_stats(stat, order):
	return map(lambda x : stat[x], order)

row_cnt = 0
def write_per_game_stats(worksheet, title, data, span, stat_func_title):
	global row_cnt
	row = row_cnt
	row_cnt = row_cnt + 1
	worksheet.write(row, 0, title)

	for i, item in enumerate(stat_func_title):
		worksheet.merge_range(row, i*span+1, row, (i+1)*span, item)

	for i, item in enumerate(data):
		worksheet.merge_range(row, (i+len(stat_func_title))*span+1, row, (i+len(stat_func_title)+1)*span, item)


def write_per_player_stats_title(worksheet, title, num_of_col):
	global row_cnt
	row = row_cnt
	row_cnt += 1
	
	worksheet.write(row, 0, "name")
	col = 0
	for i in xrange(num_of_col):
		for item in title:
			col += 1
			worksheet.write(row, col, item)

def write_per_player_stats(worksheet, player_name, player_maps, Time, stat_func):
	global row_cnt
	row = row_cnt
	row_cnt += 1

	worksheet.write(row, 0, player_name)
	col = 0
	player_map = map(lambda whole_map : whole_map[player_name], player_maps)

	range_str = "%s:%s" % (xl_rowcol_to_cell(row, len(stat_func) * len(player_map) + 1), xl_rowcol_to_cell(row, len(player_map) * (len(stat_func) + len(Time))))
	
	func = "SUM"
	for i in xrange(len(player_map)):
		col += 1
		worksheet.write_formula(row, col, "{=%s(%s * (MOD(COLUMN(%s),%d)=%d))}" % (func, range_str, range_str, len(player_map), (i + 2) % len(player_map)))
        
        for time in Time:
                for item in player_map:
                        col += 1
                        if time in item:
                                worksheet.write(row, col, item[time])
                        else:
                                worksheet.write(row, col, None)

def set_column_width(worksheet, first, next, num_of_col):
	worksheet.set_column(0, 0, first)
	col = 0
	for i in xrange(num_of_col):
		for w in next:
			col += 1
			worksheet.set_column(col, col, w)

def set_column_format(workbook, worksheet, num_item, num_time, num_stat_func, column_width):
	pass

def get_stats_from_dir(dir, workbook, worksheet):
	print "Entering", dir

	dir += '/'
	os.chdir(dir)
	files = os.listdir("./")

	Time = []
	PlayerCnt = []
	TotalGames = []
	chips_map = {}
	survival_time_map = {}
	win_by_all_in = {}
	for file in files:
		time = get_date_from_log(file)
		if time == False:
			continue

		print "Processing", file,
		fin = open(file, "r")
		
		player_count = get_player_count(fin)
		total_games = get_player_detailed_stats(fin, win_by_all_in, time)

		if total_games == -1:
			print "[RE]"
			fin.close()
			move_re_log(file)
			continue
		else:
			print
		
		Time.append(time)
		PlayerCnt.append(player_count)
		TotalGames.append(total_games)

		get_stats_of_one_item(fin, chips_map, 1, player_count, -2, 3, 'has', time)	
		get_stats_of_one_item(fin, survival_time_map, 1, player_count, -2, 3, 'has', time)

		fin.close()
	
	time_order = get_time_order(Time)
	Time = reorder_per_game_stats(Time, time_order)
	PlayerCnt = reorder_per_game_stats(PlayerCnt, time_order)
	TotalGames = reorder_per_game_stats(TotalGames, time_order)

	global row_cnt
	row_cnt = 0

	stat_func_title = ["Sum"]
	stat_func = ["SUM"]
	player_maps = [chips_map, survival_time_map, win_by_all_in]
	column_span = max(1, len(player_maps))
	column_width = [8, 12, 12] # for chips, survival_time and win_by_all_in
	set_column_width(worksheet, 12, column_width, len(Time) + len(stat_func_title))
	set_column_format(workbook, worksheet, len(player_maps), len(Time), len(stat_func_title), column_width)
	worksheet.freeze_panes(4, 1)
	
	write_per_game_stats(worksheet, "Time", Time, column_span, stat_func_title)
	write_per_game_stats(worksheet, "#Player", PlayerCnt, column_span, [''] * len(stat_func_title))
	write_per_game_stats(worksheet, "#Game", TotalGames, column_span, [''] * len(stat_func_title))

	write_per_player_stats_title(worksheet, ["Chips", "Survival time", "Win by all in"], len(Time) + len(stat_func_title))
	for name in chips_map.viewkeys():
		write_per_player_stats(worksheet, name, player_maps, Time, stat_func)

	os.chdir(pwd)

argc = len(sys.argv)
if argc < 3:
	print "Usage: <output_file_name> <directory> [...]"
	sys.exit(0)

workbook = xlsxwriter.Workbook(sys.argv[1], 
							   {"default_date_format": "mmmm d yyyy hh:mm:ss"})

for dir in sys.argv[2:]:
	get_stats_from_dir(dir, workbook, workbook.add_worksheet(dir.replace('/', '_').replace('\\','_')))

workbook.close()

