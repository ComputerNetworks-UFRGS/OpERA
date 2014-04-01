#/usr/bin/env bash

function startTest(){
    FFT=$1
    CP=$2
    EBN0=$3
    IT=$4

    echo "#### TESTING FFT=$1   CP=$2   EBN0=$3      IT=$4  ####"
    rm *.bin
    python gen_trace_file_noise.py  --fft-length $FFT  --cp-length $CP --ebn0 $EBN0 --it $IT
    python tsha_noise_preproc.py    --fft-length $FFT  --cp-length $CP --ebn0 $EBN0 --it $IT
}


for it in `seq 0 3`; do
    for ebn0 in `seq 0 11`; do
        startTest 128  9  $ebn0 $it
        #startTest 128  32  $ebn0 $it
        startTest 256  18  $ebn0 $it
        #startTest 256  64  $ebn0 $it
        startTest 512  36  $ebn0 $it
        #startTest 512  128 $ebn0 $it
        startTest 1024 108 $ebn0 $it
        #startTest 1024 256 $ebn0 $it
        startTest 2048 144 $ebn0 $it
        #startTest 2048 512 $ebn0 $it
    done
done

python tsha_file_noise.py
