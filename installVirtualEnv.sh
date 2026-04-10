#!/bin/bash
set -e
set +x

if [ -z "$PYTHON_BIN" ]; then
	PYTHON_BIN=python3
fi
PIP_OPTIONS=--no-index 
FOLDER="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
#echo $FOLDER
#exit 0
pushd ${FOLDER}

echo -e "-- Installing python3-dev"
sudo apt-get install python3-dev -y

echo -e "-- Installing python3-venv"
sudo apt-get install python3-venv -y

echo -- Installing Python Environment
${PYTHON_BIN} -m venv --system-site-packages pythonEnv

#Installing iPython
#echo -- Installing iPython
#pythonEnv\Scripts\python.exe -m pip install %PIP_OPTIONS% --find-links=file:%WORKSAPCE%\packages\IPython ipython
#pythonEnv\Scripts\python.exe -m pip install %PIP_OPTIONS% --find-links=file:%WORKSAPCE%\packages\digikey-api digikey-api
#pythonEnv\Scripts\python.exe -m pip install %PIP_OPTIONS% --find-links=file:%WORKSAPCE%\packages\octopart octopart

echo -- Installing Python Packages
pythonEnv/bin/python -m pip install -r ${FOLDER}/requirements.txt

popd
