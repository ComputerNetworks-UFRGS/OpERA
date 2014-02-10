#!/usr/bin/env bash


function startTest()
{
    IT=$1
    DUR=$2
    BURST=$3
    echo "@@@@@@@@@@@@@ PASSIVE RADIOS"
    ./interferer.py --wait-for-run 1 &
    ./radio.py --my-id 0 --sensing-duration 0.1 --sending-duration $BURST --iteration $IT&
   #./radio.py --my-id 1 --sensing-duration 0.1 --sending-duration $BURST --iteration $IT&
   #./radio.py --my-id 2 --sensing-duration 0.1 --sending-duration $BURST --iteration $IT&
    ./radio.py --my-id 3 --sensing-duration 0.1 --sending-duration $BURST --iteration $IT&
    sleep 10
    ./base_station.py --test-duration $DUR --iteration $IT --sending-duration $BURST
    sleep 10
    killall python
}


for i in `seq 0 0`; do
    startTest  $i 60 5
done
