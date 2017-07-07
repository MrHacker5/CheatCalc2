#!/bin/sh
cd /home/pi/CheatCalc2/CheatCalc/

#if false; then

SD="/home/pi/CheatCalc2/CheatCalc/shutdown.txt"
if [ -e $SD ]; then
    rm $SD
fi

python3 /home/pi/CheatCalc2/CheatCalc/cheatCalc.py

if [ -e $SD ]; then
    sudo shutdown -h now
else
    sudo shutdown -r now
fi

#fi
