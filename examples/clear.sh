#!/bin/bash

# This script clears CGRU Examples, delete rendered images and temporary scenes:

examples=`dirname $0`
cd $examples
examples=$PWD

echo "Clearing examples in '${examples}'"

script="clear.sh"

for folder in *; do
   [ -d "$folder" ] || continue
   cd "$folder"
   if [ -x "$script" ]; then
      ./$script
   fi
   cd ..
done

