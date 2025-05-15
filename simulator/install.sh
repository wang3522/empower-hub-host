#! /bin/bash
rm -rf .venv/

python3.9 -m venv .venv

source .venv/bin/activate

.venv/bin/python3 -m pip install --upgrade pip

pip3 install -r requirements.txt --break-system-packages