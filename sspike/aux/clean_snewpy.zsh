#!/bin/zsh
# Remove files created in snewpy_models directory.
source ../env.py

rm $models_dir/[A-Z]*_[1-9]*/*tar.bz2
rm $models_dir/[A-Z]*_[1-9]*/*npy
rm $models_dir/[A-Z]*_[1-9]*/*SNOprocessed.tar.gz