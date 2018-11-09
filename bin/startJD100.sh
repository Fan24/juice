#!/usr/bin/bash

baseDir="/home/ap/fan/OnionMall/"

PON_PATH=
if [ "$PYTHONPATH" = "" ];then
	PON_PATH=$baseDir
else
	PON_PATH=$PYTHONPATH:$baseDir
fi
export PYTHONPATH=$PON_PATH
export PROJ_PATH=$baseDir
cd $baseDir
srcDir="/home/ap/fan/OnionMall/gy/jd/"
pythonSrc="Dbl99Coupon.py"
dataDir="/home/ap/fan/OnionMall/data/"
logDir="/home/ap/fan/OnionMall/log/"

if [ "$1" ];then
	userFn=$1
fi
nohup python -u $srcDir$pythonSrc info.json> $logDir/JD100.log 2>&1 &
#python $srcDir$pythonSrc info.json
