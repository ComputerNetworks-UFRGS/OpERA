#!/usr/bin/env bash

function startBoth()
{
	DURATION=$1
	PKT_SIZE=$2
	ITERATION=$3
	MODE=$4
	SENDING_DUR=$5
	SENSING_DUR=$6


	echo "iteration = $ITERATION"
	echo "pkt size = $PKT_SIZE"
	echo "mode = $MODE"

	./chimas_tx.py --interferer --args addr=143.54.83.29 --log --mode $MODE --samp-rate 195512 --duration $DURATION --pkt-size $PKT_SIZE --platform tx --iteration $ITERATION --sending-duration $SENDING_DUR --sensing-duration $SENSING_DUR &

	sleep 3
	./chimas_tx.py --args addr=143.54.83.28 --log --mode $MODE --samp-rate 195512 --duration $DURATION --pkt-size $PKT_SIZE --platform tx --iteration $ITERATION --sending-duration $SENDING_DUR --sensing-duration $SENSING_DUR
	sleep 10
	killall Python
	killall python
}


for i in `seq 0 1`; do
	startBoth 3300 32 $i ss 1.0  0.1
done
