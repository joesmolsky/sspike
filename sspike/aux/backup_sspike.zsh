#!/bin/zsh
# Move all sspike outputs to backup.

TODAY=$(date +"%Y-%m-%d")
BKDIR=../../out/backup/$TODAY
mkdir $BKDIR
mv  ../../out/[A-Z]?[0-9]* $BKDIR