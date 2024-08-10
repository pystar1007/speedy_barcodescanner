#!/bin/bash
set -e

run() {

sudo apt-get update && sudo apt-get install -y libdbus-1{1,-dev}
sudo apt-get -y install python3-pip
sudo apt-get -y install omxplayer
sudo pip3 install omxplayer-wrapper

sudo apt install libsdl1.2-dev
sudo pip3 install pygame
sudo pip3 install asyncio
sudo apt-get -y install python3-pygame
sudo apt-get -y install -y libdbus-1{,-dev}


}
run
