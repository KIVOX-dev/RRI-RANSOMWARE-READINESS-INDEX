/*
 * Connection helper for the official @hyperledger/fabric-gateway Node client
 * — Fabric Gateway only ships Go/Node/Java clients, so this small service is
 * the only thing in the stack that speaks Fabric Gateway/gRPC directly. The
 * Python backend (fabric_service.py) only ever talks to this over plain
 * HTTP. Identity/connection file layout mirrors fabric-samples'
 * application-gateway-typescript reference sample.
 */
import * as grpc from '@grpc/grpc-js';
import {connect, Gateway, Identity, Signer, signers} from '@hyperledger/fabric-gateway';
import * as crypto from 'crypto';
import {promises as fs} from 'fs';
import * as path from 'path';

function envOrDefault(key: string, fallback: string): string {
    return process.env[key] ?? fallback;
}

const mspId = envOrDefault('MSP_ID', 'Org1MSP');
const cryptoPath = envOrDefault('CRYPTO_PATH', '/organizations/peerOrganizations/org1.example.com');
const keyDirectoryPath = path.resolve(cryptoPath, 'users', 'Admin@org1.example.com', 'msp', 'keystore');
const certDirectoryPath = path.resolve(cryptoPath, 'users', 'Admin@org1.example.com', 'msp', 'signcerts');
const tlsCertPath = path.resolve(cryptoPath, 'peers', 'peer0.org1.example.com', 'tls', 'ca.crt');
const peerEndpoint = envOrDefault('PEER_ENDPOINT', 'peer0.org1.example.com:7051');
const peerHostAlias = envOrDefault('PEER_HOST_ALIAS', 'peer0.org1.example.com');

async function getFirstDirFileName(dirPath: string): Promise<string> {
    const files = await fs.readdir(dirPath);
    const file = files[0];
    if (!file) {
        throw new Error(`No files in directory: ${dirPath}`);
    }
    return path.join(dirPath, file);
}

async function newIdentity(): Promise<Identity> {
    const certPath = await getFirstDirFileName(certDirectoryPath);
    const credentials = await fs.readFile(certPath);
    return {mspId, credentials};
}

async function newSigner(): Promise<Signer> {
    const keyPath = await getFirstDirFileName(keyDirectoryPath);
    const privateKeyPem = await fs.readFile(keyPath);
    const privateKey = crypto.createPrivateKey(privateKeyPem);
    return signers.newPrivateKeySigner(privateKey);
}

async function newGrpcConnection(): Promise<grpc.Client> {
    const tlsRootCert = await fs.readFile(tlsCertPath);
    const tlsCredentials = grpc.credentials.createSsl(tlsRootCert);
    return new grpc.Client(peerEndpoint, tlsCredentials, {
        'grpc.ssl_target_name_override': peerHostAlias,
    });
}

let gatewayPromise: Promise<{gateway: Gateway; client: grpc.Client}> | null = null;

// Connects lazily on first use and reuses the same gRPC connection/Gateway
// for the lifetime of the process — the Gateway API is designed to be
// shared across requests, not reconnected per call.
export function getGateway(): Promise<{gateway: Gateway; client: grpc.Client}> {
    if (!gatewayPromise) {
        gatewayPromise = (async () => {
            const client = await newGrpcConnection();
            const gateway = connect({
                client,
                identity: await newIdentity(),
                signer: await newSigner(),
                evaluateOptions: () => ({deadline: Date.now() + 5000}),
                endorseOptions: () => ({deadline: Date.now() + 15000}),
                submitOptions: () => ({deadline: Date.now() + 5000}),
                commitStatusOptions: () => ({deadline: Date.now() + 60000}),
            });
            return {gateway, client};
        })().catch((err) => {
            gatewayPromise = null;
            throw err;
        });
    }
    return gatewayPromise;
}

export const CHANNEL_NAME = envOrDefault('CHANNEL_NAME', 'rrichannel');
export const CHAINCODE_NAME = envOrDefault('CHAINCODE_NAME', 'rri-anchor');
