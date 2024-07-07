#!/bin/bash

git checkout dev
git submodule update --init --recursive
git submodule foreach git checkout master
git submodule foreach git pull

git submodule update --remote --recursive
git add biokeeper-*
git commit -m "Update submodules to latest commits"