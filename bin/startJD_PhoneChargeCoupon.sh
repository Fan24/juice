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
export VERIFY_CODE=$baseDir"input/vc.dat"
export CONF_FILE=$config_file
cd $baseDir
srcDir="/home/ap/fan/OnionMall/gy/jd/"
pythonSrc="reg_coupon.py"
dataDir="/home/ap/fan/OnionMall/data/"
logDir="/home/ap/fan/OnionMall/log/"

if [ "$1" ];then
	userFn=$1
fi
quick=false
if [ "$2" ];then
	quick=$2
fi
nohup python -u $srcDir$pythonSrc $userFn $quick> $logDir/JD_phone_charge_coupon_$userFn.log 2>&1 &
#python $srcDir$pythonSrc father.json
