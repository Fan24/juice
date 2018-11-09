#!/usr/bin/bash

baseDir="/home/ap/fan/OnionMall/"
config_file="config.json"

PON_PATH=
if [ "$PYTHONPATH" = "" ];then
	PON_PATH=$baseDir
else
	PON_PATH=$PYTHONPATH:$baseDir
fi
export PYTHONPATH=$PON_PATH
export PROJ_PATH=$baseDir
export CONF_FILE=$config_file

cd $baseDir
srcDir="/home/ap/fan/OnionMall/gy/jd/"
pythonSrc="Dbl11.py"
dataDir="/home/ap/fan/OnionMall/data/"
logDir="/home/ap/fan/OnionMall/log/"
logFile="JDDbl11.log"

if [ "$1" ];then
	userFn=$1
fi
python -u $srcDir$pythonSrc gymom.json> $logDir/$logFile 2>&1 
python -u $srcDir$pythonSrc info.json>> $logDir/$logFile 2>&1
python -u $srcDir$pythonSrc miki.json>> $logDir/$logFile 2>&1
