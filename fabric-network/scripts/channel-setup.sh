#!/usr/bin/env bash
# One-shot: runs once the orderer + peer0 are up. Creates the channel
# (orderer joins via the channel participation API, peer joins via the pre-
# built genesis block), then packages/installs/approves/commits the
# chaincode-as-a-service (CCaaS) definition — the actual chaincode server
# process runs as its own long-lived container ("chaincode" in
# docker-compose.yml), not spawned by the peer.
#
# Re-run safe: if the chaincode definition is already committed, this skips
# straight to resolving the already-approved package ID rather than
# re-packaging — `tar` output isn't byte-identical across runs, so a fresh
# package would calculate to a *different* package ID than what's actually
# committed on the channel, and the CCaaS chaincode container would then
# register under the wrong ID (found this live, not assumed).
set -euo pipefail
cd /fabric-network

CHANNEL_NAME="${CHANNEL_NAME:-rrichannel}"
CC_NAME="${CC_NAME:-rri-anchor}"
CC_VERSION="1.0"
CC_SEQUENCE="1"
CCAAS_ADDRESS="chaincode:9999"

ORG1_MSP_DIR=/fabric-network/organizations/peerOrganizations/org1.example.com
ORDERER_DIR=/fabric-network/organizations/ordererOrganizations/example.com

export FABRIC_CFG_PATH=/fabric-network/peercfg
export CORE_PEER_TLS_ENABLED=true
export CORE_PEER_LOCALMSPID=Org1MSP
export CORE_PEER_MSPCONFIGPATH=${ORG1_MSP_DIR}/users/Admin@org1.example.com/msp
export CORE_PEER_TLS_ROOTCERT_FILE=${ORG1_MSP_DIR}/peers/peer0.org1.example.com/tls/ca.crt
export CORE_PEER_ADDRESS=peer0.org1.example.com:7051
export ORDERER_CA=${ORDERER_DIR}/tlsca/tlsca.example.com-cert.pem
export ORDERER_ADMIN_TLS_SIGN_CERT=${ORDERER_DIR}/orderers/orderer.example.com/tls/server.crt
export ORDERER_ADMIN_TLS_PRIVATE_KEY=${ORDERER_DIR}/orderers/orderer.example.com/tls/server.key

BLOCKFILE="/fabric-network/channel-artifacts/${CHANNEL_NAME}.block"

echo "== Joining orderer to channel '${CHANNEL_NAME}' (channel participation API) =="
osnadmin channel join --channelID "${CHANNEL_NAME}" --config-block "${BLOCKFILE}" -o orderer.example.com:7053 --ca-file "$ORDERER_CA" --client-cert "$ORDERER_ADMIN_TLS_SIGN_CERT" --client-key "$ORDERER_ADMIN_TLS_PRIVATE_KEY" || echo "(orderer join non-fatal error, likely already joined)"

echo "== Joining peer0 to channel '${CHANNEL_NAME}' =="
if peer channel list | grep -q "^${CHANNEL_NAME}$"; then
  echo "Peer already joined."
else
  peer channel join -b "${BLOCKFILE}"
fi

ALREADY_COMMITTED=$(peer lifecycle chaincode querycommitted --channelID "${CHANNEL_NAME}" --name "${CC_NAME}" 2>/dev/null || true)

if [ -n "$ALREADY_COMMITTED" ]; then
  echo "== Chaincode definition already committed — resolving its package ID instead of repackaging =="
  echo "$ALREADY_COMMITTED"
  PACKAGE_ID=$(peer lifecycle chaincode queryapproved --channelID "${CHANNEL_NAME}" --name "${CC_NAME}" --sequence "${CC_SEQUENCE}" --output json | jq -r '.source.Type.LocalPackage.package_id')
else
  echo "== Packaging chaincode '${CC_NAME}' as chaincode-as-a-service (address ${CCAAS_ADDRESS}) =="
  PKG_DIR=$(mktemp -d)
  mkdir -p "${PKG_DIR}/src" "${PKG_DIR}/pkg"
  cat > "${PKG_DIR}/src/connection.json" <<EOF
{"address": "${CCAAS_ADDRESS}", "dial_timeout": "10s", "tls_required": false}
EOF
  LABEL="${CC_NAME}_${CC_VERSION}"
  cat > "${PKG_DIR}/pkg/metadata.json" <<EOF
{"type": "ccaas", "label": "${LABEL}"}
EOF
  # Deterministic tar output (fixed mtime/owner) so re-running this script
  # before anything is committed still calculates the same package ID.
  tar -C "${PKG_DIR}/src" --sort=name --mtime='UTC 1970-01-01' --owner=0 --group=0 --numeric-owner -czf "${PKG_DIR}/pkg/code.tar.gz" .
  tar -C "${PKG_DIR}/pkg" --sort=name --mtime='UTC 1970-01-01' --owner=0 --group=0 --numeric-owner -czf "/fabric-network/channel-artifacts/${CC_NAME}.tar.gz" metadata.json code.tar.gz
  rm -rf "${PKG_DIR}"

  PACKAGE_ID=$(peer lifecycle chaincode calculatepackageid "/fabric-network/channel-artifacts/${CC_NAME}.tar.gz")
  echo "Package ID: ${PACKAGE_ID}"

  echo "== Installing chaincode on peer0 =="
  if peer lifecycle chaincode queryinstalled --output json | grep -q "${PACKAGE_ID}"; then
    echo "Already installed."
  else
    peer lifecycle chaincode install "/fabric-network/channel-artifacts/${CC_NAME}.tar.gz"
  fi

  echo "== Approving chaincode definition for Org1 =="
  peer lifecycle chaincode approveformyorg -o orderer.example.com:7050 --ordererTLSHostnameOverride orderer.example.com --tls --cafile "$ORDERER_CA" \
    --channelID "${CHANNEL_NAME}" --name "${CC_NAME}" --version "${CC_VERSION}" --package-id "${PACKAGE_ID}" --sequence "${CC_SEQUENCE}"

  echo "== Checking commit readiness =="
  peer lifecycle chaincode checkcommitreadiness --channelID "${CHANNEL_NAME}" --name "${CC_NAME}" --version "${CC_VERSION}" --sequence "${CC_SEQUENCE}" --output json

  echo "== Committing chaincode definition =="
  peer lifecycle chaincode commit -o orderer.example.com:7050 --ordererTLSHostnameOverride orderer.example.com --tls --cafile "$ORDERER_CA" \
    --channelID "${CHANNEL_NAME}" --name "${CC_NAME}" --peerAddresses "${CORE_PEER_ADDRESS}" --tlsRootCertFiles "${CORE_PEER_TLS_ROOTCERT_FILE}" \
    --version "${CC_VERSION}" --sequence "${CC_SEQUENCE}"
fi

echo -n "${PACKAGE_ID}" > /fabric-network/channel-artifacts/chaincode-id.txt

echo "== Verifying committed definition =="
peer lifecycle chaincode querycommitted --channelID "${CHANNEL_NAME}" --name "${CC_NAME}"

echo "channel-setup complete. PACKAGE_ID=${PACKAGE_ID}"
