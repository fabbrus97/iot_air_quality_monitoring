FROM ubuntu:jammy

#dependencies
RUN apt-get update && apt-get install -y apt-utils
RUN apt-get update && apt-get install -y apt-transport-https
RUN apt-get update && apt-get install -y software-properties-common 
RUN apt-get update && apt-get install -y wget  
RUN apt-get update && apt-get install -y python3-pip  

ARG USERNAME=iot
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Create the user
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    #
    # [Optional] Add sudo support. Omit if you don't need to install software after connecting.
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# ********************************************************
# * Anything else you want to do like clean up goes here *
# ********************************************************

# [Optional] Set the default user. Omit if you want to keep the default as root.
USER $USERNAME

#install prophet
RUN pip3 install prophet
#install meteostat
RUN pip3 install meteostat
#install influx python library
RUN pip3 install influxdb_client
#install coap python library
RUN pip3 install aiocoap
#install http python library based on asyncio
RUN pip3 install aiohttp
#install telegram bot library
RUN pip3 install python-telegram-bot
RUN pip3 install requests

#TODO start coap/http server and meteostat, telegram, prophet components
