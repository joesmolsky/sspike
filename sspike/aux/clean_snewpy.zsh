#!/bin/zsh
# Script to remove files created in snewpy_models directory.
source ../env.py

rm -d $models_dir/[A-Z]*_[1-9]*/*tar.bz2
rm -d $models_dir/[A-Z]*_[1-9]*/*npy