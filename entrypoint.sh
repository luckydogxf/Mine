#!/bin/bash

set -ex

if [ ! -f "/opt/opendj/dj-data/initialized" ] ; then

        eval exec /opt/opendj/run.sh
else
        echo "Starting OpenDJ"
        # must run this, otherwise pod won't be up after rollout restart.
        echo '/opt/opendj/dj-data' > /opt/opendj/instance.loc
        eval exec /opt/opendj/bin/start-ds -N -Q

fi

