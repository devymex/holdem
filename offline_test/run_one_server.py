#!/usr/bin/python

import sys
import os
import subprocess
from datetime import datetime
import time

BIN = "./bin/"
LOG = "./log/"
MAX_GAME_CNT = 2
INITIAL_CHIPS = 3000

if sys.platform.startswith("linux") or sys.platform.startswith("darwin"):
	EXEC_SUF = ""
	MAKE = "make"
elif sys.platform == "win32":
	EXEC_SUF = ".exe"
	MAKE = "mingw32-make"
elif sys.platform == "cygwin":
	EXEC_SUF = ".exe"
	MAKE = "make"
else:
	print "UNRECOGNIZED OS"
	sys.exit(1)

argv = sys.argv
argc = len(argv)
if argc < 4:
	print "Usage: %s <server_id> <client1> <client2> [<client3> ...]" % argv[0]
	sys.exit(1)

server_id = eval(argv[1])
clients = argv[2:]
num_clients = len(clients)
port = "2014" + str(server_id)
log_dir = LOG + port + "/"

os.system("rm -rf " + log_dir)
os.system("mkdir -p " + log_dir)

null_file = open(os.devnull, "w")
login_names = []
for client in clients:
	get_login_name = subprocess.Popen(("./get_login_name" + EXEC_SUF, port), stdout = subprocess.PIPE)
	time.sleep(0.1)
	if client.endswith(".py"):
		client_proc = subprocess.Popen(("python", BIN + client, "localhost", port), stdout = null_file, stderr = subprocess.STDOUT)
	else:
		client_proc = subprocess.Popen((BIN + client, "localhost", port), stdout = null_file, stderr = subprocess.STDOUT)

	while get_login_name.poll() == None:
		if client_proc.poll() != None:
			# restart the client
			client_proc = subprocess.Popen((BIN + client, "localhost", port), stdout = null_file, stderr = subprocess.STDOUT)

	login_name = get_login_name.communicate()[0]
	try:
		client_proc.kill()
	except :
		pass
	
	p = login_name.find('\n')
	if p != -1:
		login_name = login_name[:p]

	login_names.append(login_name)

null_file.close()

name_list = []
name_list_file = open(log_dir + "name_list.txt", "w")
for client, login_name in zip(clients, login_names):
	p = client.rfind('.')
	if p == -1:
		name = client
	else:
		name = client[:p]
	name_list.append(name)
	name_list_file.write(name + " " + login_name + "\n")
	os.system("mkdir -p %s%s" % (log_dir, name))
name_list_file.close()


null_file = open(os.devnull, "w")
game_cnt = 0
in_game = [True] * num_clients
log_files = [None] * num_clients
client_procs = [None] * num_clients
while game_cnt < MAX_GAME_CNT:
	if num_clients < 2:
		print "[Server %d] fewer than 2 clients left, exit" % (server_id)
		break
	
	print "[Server %d] Starting game %d with port %s, num_clients = %d" % (server_id, game_cnt, port, num_clients)
	server_proc = subprocess.Popen(("./server", port, str(num_clients), str(INITIAL_CHIPS), "-l",  log_dir + "log", "-n", "1"), stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
	#use sed to find the player who caused the exception
	sed_proc = subprocess.Popen(("sed", "-n", "/Exception:/ {s/^.* to //; s/^.* from //; s/_[0-9]*_[0-9]*$//p}"), stdin = server_proc.stdout, stdout = subprocess.PIPE)
	server_proc.stdout.close()
	time.sleep(1) # wait for the server to start up

	now_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
	for client_id in xrange(len(clients)):
		if in_game[client_id]:
			name = name_list[client_id]
			client = clients[client_id]
			print "[Server %d] Starting client %s" % (server_id, name)
			log_file = open("%s%s/%s_%s.log" % (log_dir, name, name, now_time), "w")
			if client.endswith(".py"):
				client_proc = subprocess.Popen(("python", BIN + client, "localhost", port), stdout = log_file, stderr = subprocess.STDOUT)
			else:
				client_proc = subprocess.Popen((BIN + client, "localhost", port), stdout = log_file, stderr = subprocess.STDOUT)
			log_files[client_id] = log_file
			client_procs[client_id] = client_proc
		
	faulty_login_name = sed_proc.communicate()[0]
	if faulty_login_name != "":
		faulty_login_name = faulty_login_name.rstrip('\n')
		faulty_client_id = 0
		while faulty_client_id < len(login_names) and login_names[faulty_client_id] != faulty_login_name:
			faulty_client_id += 1
		if faulty_client_id == len(login_names):
			print "[Server %d] exception is thrown for unknown reason:" % (server_id), faulty_login_name
		else:
			print "[Server %d] %s (%s) is faulty" % (server_id, name_list[faulty_client_id], faulty_login_name)
			in_game[faulty_client_id] = False
			num_clients -= 1
	else:
		game_cnt += 1
	
	time.sleep(1) # just wait a while for the processes to quit
	for client_id in xrange(len(client_procs)):
		if client_procs[client_id] != None:
			client_proc = client_procs[client_id]
			log_file = log_files[client_id]
			if client_proc.poll() == None:
				try:
					client_proc.kill()
				except:
					pass
				log_file.write("\nProcess killed\n")
			else:
				log_file.write("\nReturns %d\n" % (client_proc.returncode))
			log_file.close()

			client_procs[client_id] = None
			log_files[client_id] = None


null_file.close()
		
print "[Server %d] game_cnt = %d" % (server_id, game_cnt)
print "[Server %d] num_clients left = %d" % (server_id, num_clients)

