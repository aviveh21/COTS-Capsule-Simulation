#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Usage: $0 ip_address [dry-run], trying default IP: 192.168.5.10"
    ip=192.168.5.10
else
    ip=$1
fi

DRY_RUN=""

if [ $# -eq 2 ]; then
    if [ "$2" = "dry-run" ]; then
    	echo "Running in dry-run mode".
    	DRY_RUN="--dry-run"
    fi
fi   

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
SSH_KEY="$SCRIPT_DIR/../keys/alex_key.pem"

RSYNC_OPTS="-avz --no-perms --no-owner --progress --no-group $DRY_RUN"

echo "Syncing local directories (no /etc /var)"
rsync $RSYNC_OPTS --exclude-from="$SCRIPT_DIR"/exclude_sync -e "ssh -i $SSH_KEY" $SCRIPT_DIR/ ubuntu@$ip:~/COTS-Capsule-Simulation/ --delete-after

echo "Syncing code (Full_detecor) .cc files"
rsync $RSYNC_OPTS  --include '*/' --include '*.cc' --exclude '*' -e "ssh -i $SSH_KEY" $SCRIPT_DIR/Full_Detector ubuntu@$ip:~/COTS-Capsule-Simulation/

echo "Syncing code (Full_detecor) .hh files"
rsync $RSYNC_OPTS  --include '*/' --include '*.hh' --exclude '*' -e "ssh -i $SSH_KEY" $SCRIPT_DIR/Full_Detector ubuntu@$ip:~/COTS-Capsule-Simulation/


echo "Syncing /etc" 
rsync $RSYNC_OPTS -e "ssh -i $SSH_KEY" --rsync-path="sudo rsync" $SCRIPT_DIR/etc/ ubuntu@$ip:/etc/

echo "Syncing /var" 
rsync $RSYNC_OPTS -e "ssh -i $SSH_KEY" --rsync-path="sudo rsync" $SCRIPT_DIR/var/ ubuntu@$ip:/var/



