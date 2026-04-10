#!/bin/bash

set -x
set -e

show_help() {
  echo -e "Usage:"
  echo -e "  -h|--help    |help"
  echo -e "  -a|--api_web |api_web"
  echo -e "  -p|--rest_api|rest_api"
  echo -e "  -w|--web     |web"
  echo -e "  -s|--start   |start"
  echo -e "  -k|--kill    |stop"
  echo -e "  -r|--restart |restart"
  echo -e "  -u|--status  |status"
}

create_log_path() {
  mkdir -p ${LOGS_PATH}
}

banner() {
  echo -e "Use: tail -f ${LOG_FILE} to see the log contain."
}

start_proc() {
  case $1 in
    api_web)
      PY_SRC=${ROOT_PATH}/Python/api_rest_service/api_rest_cors_server.py
      ARGS="--api_web --dst=api_web_output"
      ;;
    rest_api)
      PY_SRC=${ROOT_PATH}/Python/api_rest_service/api_rest_cors_server.py
      ARGS="--dst=api_rest_output -v"
      ;;
    web)
      WORKING_PATH=${ROOT_PATH}/Flask/templates
      pushd $WORKING_PATH
      PY_SRC="-m http.server" 
      ARGS=5001
  esac

  NOHUP=$2

  create_log_path
  ${NOHUP} ${PYTHON_BIN} ${PY_SRC} ${ARGS} > ${LOG_FILE} 2>&1 &
  banner
}

stop_proc() {
  case $1 in
    api_web)
      ARGS=api_web
      ;;
    rest_api)
      ARGS=api_rest_cors_server
      EXCLUDE=api_web
      ;;
    web)
      ARGS=http.server
  esac

  APP_NAME=python
  set +e
  if [ -z "$EXCLUDE" ]; then
    PID_PROC=$(ps -u | grep $APP_NAME | grep $ARGS | awk -F ' ' '{print $2}')
  else
    PID_PROC=$(ps -u | grep $APP_NAME | grep $ARGS | grep -v $EXCLUDE | awk -F ' ' '{print $2}')
  fi
  set -e

  PID_PROC=$(get_pidof $1 | awk -F ' ' '{print $3}')

  if [ ! -z "$PID_PROC" ]; then
    for PID in $PID_PROC
    do
      kill -9 $PID
    done
  fi
}

get_pidof() {
  case $1 in
    api_web)
      ARGS=api_web
      ;;
    rest_api)
      ARGS=api_rest_cors_server
      EXCLUDE=api_web
      ;;
    web)
      ARGS=http.server
  esac

  APP_NAME=python
  #killproc ${ROOT_PATH}/build/bin/${TARGET}/main_control
  set +e
  #PID_PROC=$(pidof python | grep $ARGS)
  if [ -z "$EXCLUDE" ]; then
    PIDOF_PROC=$(ps all -u $USER | grep $APP_NAME | grep $ARGS)
  else
    PIDOF_PROC=$(ps all -u $USER | grep $APP_NAME | grep $ARGS | grep -v $EXCLUDE)
  fi
  set -e
  echo -e $PIDOF_PROC
}

status_proc() {
  pidof_service=$(get_pidof $1)
  echo -e "$1 service:"
  if [ ! -z "$pidof_service" ]; then
    echo -e "${pidof_service}"
  else
    echo -e "Service stopped"
  fi
}




# --- main -----

TARGET=Debug

ROOT_PATH=$(dirname "$(readlink -f "$BASH_SOURCE")")
SPD_ROOT=$(dirname "$(readlink -f "$ROOT_PATH")")
#PARAMS="--ticks_to_msg 10 --timer_tick 100 --keep_alive_msg 3000  --config_file ./data_config/config.json"

if [ -z "$PYTHON_ENV_ROOT_" ]; then
  PYTHON_ENV_ROOT_=$(find $ROOT_PATH -name pythonEnv)
fi

if [ ! -z "$PYTHON_ENV_ROOT_" ]; then
	source $PYTHON_ENV_ROOT_/bin/activate
	PYTHON_BIN=python
else
  set +e
	PYTHON_BIN=$(which python)
  set -e
	if [ -z "$PYTHON_BIN" ]; then
		echo -e "Python not found. Please set PYTHON_ENV_ROOT_ env. Exiting with error."
		exit 1
	fi
fi

if [ -z "$PYTHON_BIN" ]; then
  echo -e "Python not found. Please set PYTHON_ENV_ROOT_ env. Exiting with error."
  exit 1
fi

$PYTHON_BIN $*

