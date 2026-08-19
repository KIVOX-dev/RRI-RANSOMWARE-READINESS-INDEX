#!/usr/bin/env sh
# The chaincode's package ID (CHAINCODE_ID) is only known once
# fabric-network/scripts/channel-setup.sh has packaged and installed it —
# wait for that file to appear (docker-compose's own depends_on already
# waits for channel-setup to *complete*, this is a belt-and-suspenders
# check for anyone running this container standalone).
set -eu
CHAINCODE_ID_FILE=/channel-artifacts/chaincode-id.txt

echo "Waiting for ${CHAINCODE_ID_FILE}..."
until [ -f "$CHAINCODE_ID_FILE" ]; do
  sleep 1
done

export CHAINCODE_ID
CHAINCODE_ID=$(cat "$CHAINCODE_ID_FILE")
export CHAINCODE_SERVER_ADDRESS="0.0.0.0:9999"

echo "Starting chaincode server, CHAINCODE_ID=${CHAINCODE_ID}"
exec npm run start:server-nontls
