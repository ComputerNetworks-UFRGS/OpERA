#!/usr/bin/env bash

if [ "$1" = "comparison" ]; then
	./plots.py --comparison
	echo 'feito'
else
	./plots.py --os $1 --duration 60 --mode txonly --sending-burst 60.0 --sensing-duration 0.0
	./plots.py --os $1 --duration 60 --mode ss     --sending-burst 2.0  --sensing-duration 0.1
	./plots.py --os $1 --duration 60 --mode ss     --sending-burst 2.0  --sensing-duration 0.5
	./plots.py --os $1 --duration 60 --mode ss     --sending-burst 2.0  --sensing-duration 1.0
fi
