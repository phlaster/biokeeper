#!/bin/bash

# Initialize submodules if not already initialized
git submodule update --init --recursive

# Fetch the latest changes for all submodules
git submodule foreach git fetch origin

# Update each submodule to the latest commit on their respective branches
git submodule update --remote --recursive

# Add the updated submodule paths to the staging area
git add .

# Commit the changes in the master repository
git commit -m "Update submodules to latest commits"

# Push the changes to the upstream repository
git push origin master