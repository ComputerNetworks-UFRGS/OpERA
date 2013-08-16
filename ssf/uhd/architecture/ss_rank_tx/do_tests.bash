#!/usr/bin/env bash

function startBoth()
{
	DURATION=$1
	PKT_SIZE=$2
	PLATFORM=$3
	ITERATION=$4
	TX_ONLY=$5

	./ss_rank_tx.py --interferer --args addr=143.54.83.29 --log $TX_ONLY --duration $DURATION --pkt-size $PKT_SIZE --platform $PLATFORM $ITERATION &

	sleep 10
	./ss_rank_tx.py --args addr=143.54.83.28 --log $TX_ONLY --duration $DURATION --pkt-size $PKT_SIZE --platform $PLATFORM $ITERATION

}

startBoth 600 1    mac 1 --tx-only
startBoth 600 256  mac 1 --tx-only
startBoth 600 512  mac 1 --tx-only
startBoth 600 1024 mac 1 --tx-only

startBoth 600 1    mac 1
startBoth 600 256  mac 1
startBoth 600 512  mac 1
startBoth 600 1024 mac 1
