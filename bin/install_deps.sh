#!/bin/sh

# install python3.5.3
pyenv install 3.5.3
# set this version as python interpreter
pyenv global 3.5.3
# Install python package
pip install -r requirements.txt

# install nodejs
apt install nodejs
# install frontend dependency
cd ./frontend/vueproj
# Install dependencies
npm install
cd -


