#!/usr/bin/env bash
# One-shot: generates MSP/TLS crypto material for Org1 + the single-node
# orderer (cryptogen), then the channel genesis block (configtxgen). Runs
# once, before the orderer/peer containers start, since they read their
# certs from disk at boot rather than waiting for them to appear.
set -euo pipefail
cd /fabric-network

CHANNEL_NAME="${CHANNEL_NAME:-rrichannel}"

if [ ! -d organizations/peerOrganizations ]; then
  echo "Generating Org1 crypto material..."
  cryptogen generate --config=./crypto-config/crypto-config-org1.yaml --output="organizations"
else
  echo "Org1 crypto material already exists, skipping cryptogen."
fi

if [ ! -d organizations/ordererOrganizations ]; then
  echo "Generating orderer crypto material..."
  cryptogen generate --config=./crypto-config/crypto-config-orderer.yaml --output="organizations"
else
  echo "Orderer crypto material already exists, skipping cryptogen."
fi

mkdir -p channel-artifacts
if [ ! -f "channel-artifacts/${CHANNEL_NAME}.block" ]; then
  echo "Generating channel genesis block for '${CHANNEL_NAME}'..."
  export FABRIC_CFG_PATH=/fabric-network/configtx
  configtxgen -profile ChannelUsingRaft -outputBlock "channel-artifacts/${CHANNEL_NAME}.block" -channelID "${CHANNEL_NAME}"
else
  echo "Channel genesis block already exists, skipping configtxgen."
fi

echo "crypto-gen complete."
