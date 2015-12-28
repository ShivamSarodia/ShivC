#!/bin/bash

find tests ! -name "*.c" -type f -delete # delete everything that's not a c file

for file in tests/*.c
do
    if [ $(python3 shivc.py $file |  grep "Done.") ]
    then
	if eval ${file%.*}
	then
	    :
	else
	    echo "${file%.*} had non-zero return code"
	fi
    else
	echo "$file failed to compile"
    fi
done
    
    
	    
