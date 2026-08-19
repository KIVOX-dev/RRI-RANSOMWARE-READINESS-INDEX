import express, {type Request, type Response} from 'express';
import {CHAINCODE_NAME, CHANNEL_NAME, getGateway} from './gateway';

const utf8Decoder = new TextDecoder();
const app = express();
app.use(express.json());

app.get('/status', async (_req: Request, res: Response) => {
    try {
        const {gateway} = await getGateway();
        const contract = gateway.getNetwork(CHANNEL_NAME).getContract(CHAINCODE_NAME);
        const resultBytes = await contract.evaluateTransaction('anchorCount');
        const anchorCount = parseInt(utf8Decoder.decode(resultBytes), 10);
        res.json({connected: true, anchor_count: anchorCount});
    } catch (err) {
        res.json({connected: false, anchor_count: null, error: String(err)});
    }
});

app.post('/anchor', async (req: Request, res: Response) => {
    const recordHash = req.body?.record_hash;
    if (typeof recordHash !== 'string' || recordHash.length === 0) {
        res.status(400).json({error: 'record_hash is required'});
        return;
    }
    try {
        const {gateway} = await getGateway();
        const contract = gateway.getNetwork(CHANNEL_NAME).getContract(CHAINCODE_NAME);
        const commit = await contract.submitAsync('anchorAssessment', {arguments: [recordHash]});
        const status = await commit.getStatus();
        if (!status.successful) {
            res.status(502).json({error: `transaction ${status.transactionId} failed to commit with code ${String(status.code)}`});
            return;
        }
        res.json({tx_id: status.transactionId});
    } catch (err) {
        res.status(503).json({error: String(err)});
    }
});

const port = Number(process.env.PORT ?? 3001);
app.listen(port, () => {
    console.log(`fabric-gateway-api listening on :${port}`);
});
