#!/bin/bash

# Runs through the filter and response files, changing 
# format_version from $old_version to $new_version
old_version="0.103"
new_version="0.104"
for d in DataLoggers PreAmplifiers Sensors _filters/*; do
    for f in $d/*.yaml; do
        echo $f
        sed "/format_version/s/\"$old_version\"/\"$new_version\"/g" $f > temp
        mv temp $f
    done
done
