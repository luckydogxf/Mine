#!/usr/bin/env bash

set -ex

cd /opt/opendj

echo "Setting up default OpenDJ instance"

#export DEPLOYMENT_ID=`./bin/dskeymgr create-deployment-id --deploymentIdPassword  whatever-password`
export DEPLOYMENT_ID="ANhe68wg8C_0K628hrOSUEungCQzmlw5CBVN1bkVDeqiFk3uS_02Prtw"

#./bin/setup-profile --profile ds-evaluation --set ds-evaluation/generatedUsers:50

./setup  --serverId pacific-opendj-1  --deploymentId $DEPLOYMENT_ID  --deploymentIdPassword 49Pn0pzaVr8w --rootUserDN cn=Administrator  --rootUserPassword $ROOT_PASSWORD  --monitorUserPassword $ROOT_PASSWOR
D  --hostname localhost  --adminConnectorPort 4444  --ldapPort 19389   --ldapsPort 1636  --httpsPort 8443  --httpPort=8080 --replicationPort 8989  --bootstrapReplicationServer localhost:8989     --acceptLic
ense --enableStartTls  --profile ds-user-data:7.0.0 --set ds-user-data/baseDn:$BASE_DN -Q --instancePath /opt/opendj/dj-data

touch /opt/opendj/dj-data/initialized

sed -i "s/default.java-args=-server -Xms256m -Xmx256m/default.java-args=-server -Xms${JAVA_JVM} -Xmx${JAVA_JVM}/" /opt/opendj/dj-data/config/java.properties

ln -sf /dev/stdout /opt/opendj/dj-data/logs/server.out  && ln -sf /dev/stderr /opt/opendj/dj-data/logs/errors

echo '/opt/opendj/dj-data' > /opt/opendj/instance.loc

# start opendj

eval exec ./bin/start-ds -N -Q

##### manually execution ###

#./bin/dsconfig set-password-policy-prop --policy-name "Default Password Policy" \
#       --hostname=localhost --port 4444 --bindDN cn=Administrator --bindPassword xyzabc_123 \
#       --advanced --set allow-pre-encoded-passwords:true  --no-prompt --trustAll
