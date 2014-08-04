#!/bin/bash

if [[ $# != 3 ]]; then
	echo "Usage: ./run_server <port> <numPlayers> <log_folder>"
	exit 1
fi

mkdir -p $3
./server $1 $2 3000 $3/log
