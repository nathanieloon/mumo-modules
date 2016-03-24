#!/bin/bash
# This script creates links for each of the components for the modules
echo Creating links for modules
cd ../mumo/modules && ln -s ../../mumo-modules/bot.py && cd -
cd ../mumo/modules && ln -s ../../mumo-modules/dbintegrate.py && cd -
cd ../mumo/modules && ln -s ../../mumo-modules/setstatus.py && cd -
cd ../mumo/modules && ln -s ../../mumo-modules/urltoimg.py && cd -

echo Creating links for modules-available
cd ../mumo/modules-available && ln -s ../../mumo-modules/bot.ini && cd -
cd ../mumo/modules-available && ln -s ../../mumo-modules/dbintegrate.ini && cd -
cd ../mumo/modules-available && ln -s ../../mumo-modules/setstatus.ini && cd -
cd ../mumo/modules-available && ln -s ../../mumo-modules/urltoimg.ini && cd -

echo Creating links for modules-enabled
cd ../mumo/modules-enabled && ln -s ../../mumo-modules/bot.ini && cd -
cd ../mumo/modules-enabled && ln -s ../../mumo-modules/dbintegrate.ini && cd -
cd ../mumo/modules-enabled && ln -s ../../mumo-modules/setstatus.ini && cd -
cd ../mumo/modules-enabled && ln -s ../../mumo-modules/urltoimg.ini && cd -