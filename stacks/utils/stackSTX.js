import { getNonce } from '@stacks/transactions'
import { StacksTestnet, StacksMainnet } from '@stacks/network'
import { StackingClient } from '@stacks/stacking'
import dotenv from 'dotenv'
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const __envpath__ = path.resolve(__dirname, "../config/.env")
dotenv.config({ path: __envpath__ }) // Read env variables from .env
const poolPrivateKey = process.env.poolPrivateKey
const poolSTXAddress = process.env.poolSTXAddress
const poolBTCAddress = process.env.poolBTCAddress

const network = new StacksMainnet() // for mainnet
// const network = new StacksTestnet() // for testnet
// network.coreApiUrl = 'http://127.0.0.1:3999' // local Stack API server

const myArgs = process.argv.slice(2);
const newVoters = myArgs[0]
const voters = JSON.parse(newVoters)

function sleep(seconds) {
    return new Promise(resolve => setTimeout(resolve, seconds * 1000))
}

let txids = [];
let chunk = 20;
let blockHeight = 0

for (let i = 0; i < voters.length; i += chunk) {
    let votersChunk = voters.slice(i, i + chunk);

    const delegatorClient = new StackingClient(poolSTXAddress, network)
    let coreInfo = await delegatorClient.getCoreInfo()
    let newBlockHeight = coreInfo['stacks_tip_height']

    while (blockHeight === newBlockHeight) {
        let coreInfo = await delegatorClient.getCoreInfo()
        newBlockHeight = coreInfo['stacks_tip_height']
        if (newBlockHeight > blockHeight) {
            break
        }
        console.log('Current block height is:', newBlockHeight, ' Checking again in 10 minutes.');
        await sleep(10 * 60)
    }
    blockHeight = newBlockHeight
    console.log('Stacking voters to block: ', blockHeight);
    for (let j = 0; j < votersChunk.length; j++) {
        const voter = votersChunk[j]
        const voterAddress = voter.voterAddress
        const cycleCommitted = voter.cycleCommitted
        const lockingCycles = voter.lockingCycles
        const stackedMicroSTX = BigInt(voter.stackedSTX * 1000000)

        const poxInfo = await delegatorClient.getPoxInfo()
        const nextCycle = poxInfo['reward_cycle_id'] + 1
        const remainingCycles = (cycleCommitted + lockingCycles) - nextCycle

        // Stack voter if remainingCycles is greater than or equal to 0, or cycleCommitted is less than or equal to currentCycle
        if (remainingCycles >= 0) {
            let nonce = await getNonce(poolSTXAddress, network)
            let newNonce = BigInt(i)
            nonce = nonce + newNonce;
            let coreInfo = await delegatorClient.getCoreInfo()
            let burnBlockHeight = coreInfo['burn_block_height'] + 3 // BTC block height at which to stack

            const delegetateStackResponses = await delegatorClient.delegateStackStx({
                stacker: voterAddress,
                amountMicroStx: stackedMicroSTX,
                poxAddress: poolBTCAddress,
                burnBlockHeight,
                cycles: lockingCycles,
                privateKey: poolPrivateKey,
                nonce, // optional
            })
            txids.push(delegetateStackResponses)
        }
    }

}

console.log(JSON.stringify(txids))

