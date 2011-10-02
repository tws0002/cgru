#!/bin/bash

# Source general for all soft directives:
source "$CGRU_LOCATION/software_setup/setup__all.sh"

# Search directory where Houdini installed:
HOUDINI_INSTALL_DIR="/opt"
for folder in `ls "$HOUDINI_INSTALL_DIR"`; do
   if [ "`echo $folder | awk '{print match( \$1, "hfs")}'`" == "1" ]; then
      export HOUDINI_LOCATION="${HOUDINI_INSTALL_DIR}/${folder}"
   fi
done

# Overrides (set custom values there):
[ -f override.sh ] && source override.sh

# Check Houdini location:
if [ -z "$HOUDINI_LOCATION" ]; then
   echo "Can't find houdini in '$HOUDINI_DIR'"
   exit 1
fi
echo "Houdni location = '$HOUDINI_LOCATION'"

# Source Houdini setup shell script:
pushd $HOUDINI_LOCATION >> /dev/null
source houdini_setup_bash
popd $pwd >> /dev/null

# Setup CGRU houdini scripts location:
export HOUDINI_CGRU_PATH=$CGRU_LOCATION/plugins/houdini

# Set Afanasy houdini scripts and otls location:
export HOUDINI_AF_PATH=$AF_ROOT/plugins/houdini

# Set Python path to afanasy submission script:
export PYTHONPATH=$HOUDINI_AF_PATH:$PYTHONPATH

# Define OTL scan path:
HOUDINI_AF_OTLSCAN_PATH=$HIH/otls:$HOUDINI_AF_PATH:$HH/otls

# Create or add to exist OTL scan path:
if [ "$HOUDINI_OTLSCAN_PATH" != "" ]; then
   export HOUDINI_OTLSCAN_PATH="${HOUDINI_AF_OTLSCAN_PATH}:${HOUDINI_OTLSCAN_PATH}"
else
   export HOUDINI_OTLSCAN_PATH=$HOUDINI_AF_OTLSCAN_PATH
fi

# Try CGRU 2.6 Python (Houdini 11 uses 2.6 Python):
cgru_python="$CGRU_LOCATION/utilities/python/2.6.7"
if [ -d $cgru_python ]; then
   echo "Using CGRU Python = '$cgru_python'"
   export PYTHONHOME=$cgru_python
   export PATH=$cgru_python/bin:$PATH
   export PYTHONPATH=$AF_ROOT/bin_pyaf/2.6.7:$PYTHONPATH
fi

export APP_DIR="$HOUDINI_LOCATION"
export APP_EXE="houdini"
