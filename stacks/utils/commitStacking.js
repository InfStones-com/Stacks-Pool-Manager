import { StacksTestnet, StacksMainnet } from '@stacks/network'
import { StackingClient } from '@stacks/stacking'
import BN from 'bn.js'
import dotenv from 'dotenv'
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const __envpath__ = path.resolve(__dirname, "../config/.env")
dotenv.config({ path: __envpath__ }) // Read env variables from .env
const poolSTXAddress = process.env.poolSTXAddress
const poolPrivateKey = process.env.poolPrivateKey
const poolBTCAddress = process.env.poolBTCAddress

const network = new StacksMainnet() // for mainnet
//const network = new StacksTestnet() // for testnet
// network.coreApiUrl = 'http://127.0.0.1:3999' // local Stack API server

const delegatorClient = new StackingClient(poolSTXAddress, network)

let rewardCycle, delegetateCommitResponse, poxInfo
poxInfo = await delegatorClient.getPoxInfo()
rewardCycle = poxInfo['reward_cycle_id'] + 1

console.log("Start aggregate commit for cycle:", rewardCycle)
delegetateCommitResponse = await delegatorClient.stackAggregationCommit({
    poxAddress: poolBTCAddress, // this must be the delegator bitcoin address
    rewardCycle,
    privateKey: poolPrivateKey,
})
console.log('Done aggregate commit. The delegetateCommitResponse: ', delegetateCommitResponse)
