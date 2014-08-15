#!/bin/bash

#set -x

rm -rf tmp
rm -rf bin
mkdir -p bin

client_path="../client"

if [[ ${OSTYPE} == "linux-gnu" || ${OSTYPE} == "darwin"*  ]]; then
	MAKE=make
	MAKEFILE=Makefile
	EXEC_SUFFIX=""
elif [[ ${OSTYPE} == "msys" ]]; then
	MAKE=mingw32-make
	MAKEFILE=Makefile-mingw
	EXEC_SUFFIX=.exe
elif [[ ${OSTYPE} == "cygwin" ]]; then
	echo "CANNOT run in cygwin"
	exit 1
else
	echo "UNKNOWN OS"
	exit 1
fi

for zip_file in `ls *.zip`
do
	name=`echo ${zip_file} | sed 's/\.zip//'`
	echo "======================================="
	unzip -o ${name}.zip

	if [[ ! -e ${name} ]]; then
		echo "[ERROR] file not found"
		rm -rf ${name}
		continue
	fi

	if [[ `ls ${name}/*.cpp 2>/dev/null` ]]; then
		echo "cpp found, compiling"
		mkdir tmp
		cp -f ${client_path}/*.h tmp/
		cp -f ${client_path}/*.cpp tmp/
		cp -f ${client_path}/${MAKEFILE} tmp/Makefile-template
		cp -f ${name}/*.cpp tmp/
		cp -f ${name}/*.h tmp/
		
		cd ${name}
		AI=$(ls *.cpp | sed -n -e 's/.cpp//p' -e 'q')
		cd ..
		if [[ ! ${AI} ]]; then
			echo "AI is not properly set"
		else
			cd tmp
			sed 's/AI = example/AI = '${AI}'/' Makefile-template > Makefile
			${MAKE} 

			if [[ $? -eq 0 ]]; then
				cp -f ./client${EXEC_SUFFIX} ../bin/${name}${EXEC_SUFFIX}
			else
				echo "compile error"
			fi
			cd ..
			rm -rf tmp
		fi
	elif [[ `ls ${name}/*.py 2>/dev/null` ]]; then
		echo "py found, copying"
		cp -f `ls ${name}/*.py` bin/${name}.py
	else
		echo "no implementation found"
	fi

	rm -rf ${name}
done
