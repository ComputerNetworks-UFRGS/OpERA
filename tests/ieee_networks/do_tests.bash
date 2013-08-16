#!/usr/bin/env bash

# Syntax:
# start both <total duration> <pkt size> <platform> <iteration> <mode> <sending dur> <sensing dur>
# where:
# <total duration> is the total test time
# <pkt size> is the packet size in bytes
# <platform> specifies you computer (for log only)
# <iteration> is the iteration executed (for log only)
# <mode> is either txonly (for transmission only - without channel switches) of ss (with transmission, sensing and channel switching)
# <sending dur> is the interval to transmit packets
# <sensing dur> is the interval to sense the channel
function startBoth()
{
	DURATION=$1
	PKT_SIZE=$2
	PLATFORM=$3
	ITERATION=$4
	MODE=$5
	SENDING_DUR=$6
	SENSING_DUR=$7


	echo "************** Starting new test *******************"
	echo "DURATION  = $DURATION"
	echo "PLATFORM  = $PLATFORM"
	echo "ITERATION = $ITERATION"
	echo "PKT SIZE  = $PKT_SIZE"
	echo "MODE      = $MODE"
	echo "SS DUR    = $SENSING_DUR"
	echo "TX DUR    = $SENDING_DUR"

	# Change the RECEIVER USRP IP address if needed
	./ss_rank_tx.py --interferer --args addr=143.54.83.29 --log --mode $MODE --samp-rate 1e6 --duration $DURATION --pkt-size $PKT_SIZE --platform $PLATFORM --iteration $ITERATION --sending-duration $SENDING_DUR --sensing-duration $SENSING_DUR &

	sleep 3
	# Change the CSA USRP IP address if needed
	./ss_rank_tx.py --args addr=143.54.83.28 --log --mode $MODE --samp-rate 1e6 --duration $DURATION --pkt-size $PKT_SIZE --platform $PLATFORM --iteration $ITERATION --sending-duration $SENDING_DUR --sensing-duration $SENSING_DUR
	sleep 10
	killall Python
	killall python
}


# TOTAL NUMBER OF TEST REPETITIONS
for i in `seq 0 20`; do
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

# PLOT SOME INITIAL GRAPHS
./plots.py --os $1 --duration 60 --mode txonly --sending-burst 60.0 --sensing-duration 0.0
./plots.py --os $1 --duration 60 --mode ss     --sending-burst 2.0  --sensing-duration 0.1
./plots.py --os $1 --duration 60 --mode ss     --sending-burst 2.0  --sensing-duration 0.5
./plots.py --os $1 --duration 60 --mode ss     --sending-burst 2.0  --sensing-duration 1.0
