#!/usr/bin/env bash


function startTest()
{
    IT=$1
    EBN0=$2

    python noise.py --it $IT --ebn0 $EBN0
}


for ebn0 in `seq -20 1 20`; do
    for i in `seq 0 0`; do
        startTest  $i $ebn0
    done
done

