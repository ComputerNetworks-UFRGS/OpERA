#!/usr/bin/env bash


function startTest()
{
    IT=$1
    DUR=$2
    BURST=$3
    ALGO=$4
    echo "@@@@@@@@@@@@@ PASSIVE RADIOS"
    ./radio.py --algo-name $ALGO --my-id 0 --sensing-duration 0.1 --sending-duration $BURST --iteration $IT&
    ./radio.py --algo-name $ALGO --my-id 1 --sensing-duration 0.1 --sending-duration $BURST --iteration $IT&
    ./radio.py --algo-name $ALGO --my-id 2 --sensing-duration 0.1 --sending-duration $BURST --iteration $IT&
    ./radio.py --algo-name $ALGO --my-id 3 --sensing-duration 0.1 --sending-duration $BURST --iteration $IT&
    sleep 10
    ./base_station.py --test-duration $DUR --algo-name $ALGO --iteration $IT --sending-duration $BURST
    sleep 10
    killall python
}


for i in `seq 0 0`; do
    #startTest $i 3600 5 simple
    #startTest $i 3600 5 fuzzy
    #startTest  $i 3600 5 graph
    #startTest  $i 60 5 genetic
    #startTest  $i 60 5 sim_annealing
    startTest  $i 60 5 blp
done
