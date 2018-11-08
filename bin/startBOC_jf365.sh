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
srcDir="/home/ap/fan/OnionMall/gy/boc/"
pythonSrc="jf365.py"
dataDir="/home/ap/fan/OnionMall/data/"
logDir="/home/ap/fan/OnionMall/log/"

if [ "$1" ];then
	userFn=$1
fi
nohup python -u $srcDir$pythonSrc > $logDir/boc_jf365.log 2>&1 &
#python $srcDir$pythonSrc 
