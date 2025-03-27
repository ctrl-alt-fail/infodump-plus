#!/usr/bin/env bash

###################################################################
# SCRIPT NAME       : infodump
# DESCRIPTION       : Script to output common useful information about a System Node.
# 
# AUTHOR            : Joseph S Fleet
# EMAIL             : josephsfleet@gmail.com
###################################################################

### Colour Definitions ###

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
WHITE='\033[0;37m'
RESET='\033[0m'
BGGREEN='\033[42m'

##########################

clear

echo -e "${BGGREEN}|-------------------------SYSTEM INFO------------------------|${RESET}"

echo "Current Dir: $(pwd)"
echo -e "whoami: ${RED}$(whoami)${RESET}"
echo -e "Hostname: ${BLUE}$(uname -n)${RESET}"
echo -e "Kernel Version: $(uname -r)"
echo -e "${RED}$(timedatectl status)${RESET}"
echo -e "System Language: ${BLUE}$LANG${RESET}"

echo -e "${BGGREEN}|---------------------------NETWORK--------------------------|${RESET}"

if ping -c 1 1.1.1.1 &> /dev/null
then
    echo -e "${GREEN}Outbound connection successful.${RESET}"
else
    echo -e "${RED}Outbound connection ERROR.${RESET}" 
fi
echo -e "NIC Info: ${YELLOW}$(ip a | grep "eno\|enp" | cut -d ':' -f 2-3)${RESET}"

echo -e "${BGGREEN}|------------------------MEMORY USAGE------------------------|${RESET}"

echo -e "$(free -h)"

echo -e "${BGGREEN}|------------------------SYSTEM DISKS------------------------|${RESET}"

df -h

echo -e "${BGGREEN}|----------------------(3) LARGEST FILES---------------------|${RESET}"

echo -e "${RED}$(find /home -type f -printf '%s %p\n' 2> /dev/null | sort -nr | head -3 | xargs ls -lh 2> /dev/null | cut -d ' ' -f 5,9)${RESET}"

echo -e "${BGGREEN}|-------------------(3) HIGH CPU PROCESSES-------------------|${RESET}"

ps -eo pid,ppid,cmd,%mem,%cpu --sort=-%cpu | head -4

echo -e "${BGGREEN}|-----------------------------END----------------------------|${RESET}"
