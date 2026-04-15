#!/bin/bash

set -x
set -e

./run_python.sh generar_pdf.py

./run_python.sh gen_foto_carnet.py

