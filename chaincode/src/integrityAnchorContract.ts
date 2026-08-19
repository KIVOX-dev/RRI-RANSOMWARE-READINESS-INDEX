/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * Minimal on-chain anchor for RRI's Integrity Ledger. This is a stretch/demo
 * layer on top of the application's default integrity mechanism (a signed,
 * off-chain SHA-256 hash chain — see backend/app/services/ledger_service.py).
 * Each call records only a 32-byte hash and a timestamp; no assessment data,
 * evidence, or personal information is ever written on-chain. Mirrors the
 * previous IntegrityAnchor.sol contract's semantics (anchorAssessment /
 * getAnchor / anchorCount) so the rest of the system's mental model didn't
 * need to change when the chain moved from Besu (EVM/Solidity) to Fabric.
 */
import {Context, Contract, Info, Returns, Transaction} from 'fabric-contract-api';

const COUNT_KEY = 'ANCHOR_COUNT';

interface Anchor {
    recordHash: string;
    timestamp: string;
    anchoredBy: string;
}

@Info({title: 'IntegrityAnchor', description: 'On-chain anchor for RRI Integrity Ledger record hashes'})
export class IntegrityAnchorContract extends Contract {

    @Transaction()
    @Returns('number')
    public async anchorAssessment(ctx: Context, recordHash: string): Promise<number> {
        const countBytes = await ctx.stub.getState(COUNT_KEY);
        const index = countBytes.length === 0 ? 0 : parseInt(countBytes.toString(), 10);

        const txTimestamp = ctx.stub.getTxTimestamp();
        const millis = Number(txTimestamp.seconds) * 1000 + Math.floor(txTimestamp.nanos / 1e6);
        const anchor: Anchor = {
            recordHash,
            timestamp: new Date(millis).toISOString(),
            anchoredBy: ctx.clientIdentity.getID(),
        };

        await ctx.stub.putState(`ANCHOR_${index}`, Buffer.from(JSON.stringify(anchor)));
        await ctx.stub.putState(COUNT_KEY, Buffer.from(String(index + 1)));

        return index;
    }

    @Transaction(false)
    @Returns('string')
    public async getAnchor(ctx: Context, index: number): Promise<string> {
        const bytes = await ctx.stub.getState(`ANCHOR_${index}`);
        if (bytes.length === 0) {
            throw new Error(`No anchor at index ${index}`);
        }
        return bytes.toString();
    }

    @Transaction(false)
    @Returns('number')
    public async anchorCount(ctx: Context): Promise<number> {
        const countBytes = await ctx.stub.getState(COUNT_KEY);
        return countBytes.length === 0 ? 0 : parseInt(countBytes.toString(), 10);
    }
}
