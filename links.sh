#!/bin/bash
# This script creates links for each of the components for the modules
echo "Creating links for modules"
cd ../mumo/modules && ln -s ../../mumo-modules/bot.py
cd ../../mumo-modules
cd ../mumo/modules && ln -s ../../mumo-modules/dbintegrate.py
cd ../../mumo-modules
cd ../mumo/modules && ln -s ../../mumo-modules/setstatus.py 
cd ../../mumo-modules
cd ../mumo/modules && ln -s ../../mumo-modules/urltoimg.py 
cd ../../mumo-modules

echo "Creating links for modules-available"
cd ../mumo/modules-available && ln -s ../../mumo-modules/bot.ini 
cd ../../mumo-modules
cd ../mumo/modules-available && ln -s ../../mumo-modules/dbintegrate.ini 
cd ../../mumo-modules
cd ../mumo/modules-available && ln -s ../../mumo-modules/setstatus.ini 
cd ../../mumo-modules
cd ../mumo/modules-available && ln -s ../../mumo-modules/urltoimg.ini 
cd ../../mumo-modules

echo "Creating links for modules-enabled"
cd ../mumo/modules-enabled && ln -s ../modules-available/bot.ini 
cd ../../mumo-modules
cd ../mumo/modules-enabled && ln -s ../modules-available/dbintegrate.ini 
cd ../../mumo-modules
cd ../mumo/modules-enabled && ln -s ../modules-available/setstatus.ini 
cd ../../mumo-modules
cd ../mumo/modules-enabled && ln -s ../modules-available/urltoimg.ini 
cd ../../mumo-modules
cd ../mumo/modules-enabled && ln -s ../modules-available/seen.ini 
cd ../../mumo-modules
