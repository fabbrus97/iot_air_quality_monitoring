#!/bin/bash

if [ "$1" == "-r"  ] ; then
  echo "removing dataproxy image" ; docker image rm -f dataproxy 2> /dev/null
  echo "removing datanalytics image" ; docker image rm -f dataanalytics 2> /dev/null
  echo "removing extra_telegram image" ; docker image rm -f extra_telegram 2> /dev/null
  echo "removing extra_meteo image" ; docker image rm -f extra_meteo 2> /dev/null
fi

echo "building dataproxy image" ; docker build -t dataproxy -f 1_data_proxy/Dockerfile . 1> /dev/null 
echo "building datanalytics image" ; docker build -t dataanalytics -f 3_data_analytics/Dockerfile . 1> /dev/null
echo "building extra_telegram image" ; docker build -t extra_telegram -f extra/Dockerfile_telegram . 1> /dev/null
echo "building extra_meteo image" ; docker build -t extra_meteo -f extra/Dockerfile_meteo . 1> /dev/null
