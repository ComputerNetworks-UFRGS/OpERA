#!/usr/bin/env bash


function startTest()
{
    IT=$1
    EBN0=$2

    PH1=0.9

    python ata --it $IT --ebn0 $EBN0 --ph1 $PH1 --sensing cyclostationary
    python tsha.py --it $IT --ebn0 $EBN0 --ph1 $PH1 --sensing cyclostationary
}


for i in `seq 0 20`; do
    for ebn0 in `seq -20 1 5`; do
            startTest  $i $ebn0
    done
done
