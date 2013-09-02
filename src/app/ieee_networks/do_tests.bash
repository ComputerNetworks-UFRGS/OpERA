#!/usr/bin/env bash

function startBoth()
{
	DURATION=$1
	PKT_SIZE=$2
	PLATFORM=$3
	ITERATION=$4
	MODE=$5
	SENDING_DUR=$6
	SENSING_DUR=$7


	echo "iteration = $ITERATION"
	echo "pkt size = $PKT_SIZE"
	echo "mode = $MODE"

	./ss_rank_tx.py --interferer --args addr=143.54.83.29 --log --mode $MODE --samp-rate 3e6 --duration $DURATION --pkt-size $PKT_SIZE --platform $PLATFORM --iteration $ITERATION --sending-duration $SENDING_DUR --sensing-duration $SENSING_DUR &

	sleep 3
	./ss_rank_tx.py --args addr=143.54.83.28 --log --mode $MODE --samp-rate 3e6 --duration $DURATION --pkt-size $PKT_SIZE --platform $PLATFORM --iteration $ITERATION --sending-duration $SENDING_DUR --sensing-duration $SENSING_DUR
	sleep 10
	killall Python
	killall python
}


for i in `seq 0 4`; do
	echo ''
	startBoth 60 32   $1 $i txonly 60 0.0
	startBoth 60 64   $1 $i txonly 60 0.0
	startBoth 60 128  $1 $i txonly 60 0.0
	startBoth 60 256  $1 $i txonly 60 0.0
	startBoth 60 512  $1 $i txonly 60 0.0
	startBoth 60 1024 $1 $i txonly 60 0.0
	startBoth 60 2048 $1 $i txonly 60 0.0
	startBoth 60 4096 $1 $i txonly 60 0.0

	startBoth 60 32   $1 $i ss 2 0.1
	startBoth 60 64   $1 $i ss 2 0.1
	startBoth 60 128  $1 $i ss 2 0.1
	startBoth 60 256  $1 $i ss 2 0.1
	startBoth 60 512  $1 $i ss 2 0.1
	startBoth 60 1024 $1 $i ss 2 0.1
	startBoth 60 2048 $1 $i ss 2 0.1
	startBoth 60 4096 $1 $i ss 2 0.1

	startBoth 60 32   $1 $i ss 2 0.5
	startBoth 60 64   $1 $i ss 2 0.5
	startBoth 60 128  $1 $i ss 2 0.5
	startBoth 60 256  $1 $i ss 2 0.5
	startBoth 60 512  $1 $i ss 2 0.5
	startBoth 60 1024 $1 $i ss 2 0.5
	startBoth 60 2048 $1 $i ss 2 0.5
	startBoth 60 4096 $1 $i ss 2 0.5

	startBoth 60 32   $1 $i ss 2 1.0
	startBoth 60 64   $1 $i ss 2 1.0
	startBoth 60 128  $1 $i ss 2 1.0
	startBoth 60 256  $1 $i ss 2 1.0
	startBoth 60 512  $1 $i ss 2 1.0
	startBoth 60 1024 $1 $i ss 2 1.0
	startBoth 60 2048 $1 $i ss 2 1.0
	startBoth 60 4096 $1 $i ss 2 1.0
done

./plots.py --os $1 --duration 60 --mode txonly --sending-burst 60.0 --sensing-duration 0.0
./plots.py --os $1 --duration 60 --mode ss     --sending-burst 2.0  --sensing-duration 0.1
./plots.py --os $1 --duration 60 --mode ss     --sending-burst 2.0  --sensing-duration 0.5
./plots.py --os $1 --duration 60 --mode ss     --sending-burst 2.0  --sensing-duration 1.0
