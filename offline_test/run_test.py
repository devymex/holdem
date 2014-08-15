#!/usr/bin/python

import os
import sys
from datetime import datetime
import subprocess

server_path="../server/"
client_paht="../client/"
CLIENT = "client"
SERVER = "server"

NUM_SERVER = 3

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

CLIENT = CLIENT + EXEC_SUF
SERVER = SERVER + EXEC_SUF

argc = len(sys.argv)
argv = sys.argv
if argc > 1:
	if argv[1] == "clean":
		os.system("rm -rf bin/")
		os.system("rm -rf log/")
		os.system("rm -f " + SERVER)
		os.system("rm -f get_stat.py")
		os.system("make clean")
		sys.exit(0)
	elif argv[1] == "help":
		print "Usage: %s [clean | help]" % argv[0]

os.system("mkdir -p log/")
if not os.access("./bin/", os.F_OK):
	print "Building AIs"
	if sys.platform == "cygwin":
		print "[ERROR] cannot build in cygwin"
		sys.exit(1)
	os.system("./build_all.sh | tee log/build.log")
	print 

if not os.access(SERVER, os.F_OK):
	print "Building server"
	os.system(MAKE + " -C "  + server_path)	
	os.system("cp -f " + server_path + SERVER + " ./")
	os.system("cp -f " + server_path + "get_stat.py ./")
	os.system("make get_login_name" + EXEC_SUF);

bin_list = os.listdir("./bin/")
if len(bin_list) < 2 * NUM_SERVER:
	print "Too few player to start %d server (got %d, need >= %d)" % (NUM_SERVER, len(bin_list), 2 * NUM_SERVER)
	sys.exit(1)

clients = []
now = 0
avg_player_per_server = len(bin_list) / NUM_SERVER
for i in xrange(NUM_SERVER):
	end = now + avg_player_per_server
	if i < len(bin_list) - NUM_SERVER * avg_player_per_server:
		end += 1
	if end > len(bin_list):
		end = len(bin_list)
	clients.append(bin_list[now:end])
	now = end

server_procs = []
for server_id, client_list in enumerate(clients):
	server_id += 1
	command = ["python", "run_one_server.py", str(server_id)]
	command.extend(client_list)
	server_procs.append(subprocess.Popen(command))

for server_proc in server_procs:
	server_proc.wait()

## get stats
os.system("cp -f get_stat.py log/")
os.chdir("log")
command = ["python", "get_stat.py", "scoreboard.xlsx"]
for i in xrange(1, NUM_SERVER + 1):
	command.append("2014" + str(i))
subprocess.Popen(command).wait()
os.system("rm -f get_stat.py")
os.chdir("../")
	

