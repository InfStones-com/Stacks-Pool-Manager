# Stacks-Pool-Manager


<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#configurations">Configurations</a></li>
      </ul>
    </li>
    <li>
      <a href="#usage">Usage</a></li>
      <ul>
        <li><a href="#runpool">runPool</a></li>
        <li><a href="#calculatematching">calculateMatching</a></li>
        <li><a href="#calculaterewards">calculateRewards</a></li>
      </ul>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>


<!-- ABOUT THE PROJECT -->
## About The Project

This Pool Manager was a collaborative project that we started with the STX team. The STX team wanted to work alongside with InfStones team to design and launch an open-source do-it-yourself Stacking pool manager. When launched, it will make it easy for individuals or businesses to create and manage their own Stacking pools.

The two teams designed these pools being used in a variety of ways, including by future Stacks Chapters, teams or developers raising funding, charitable efforts, and much more. The tool will work via delegation so pool managers do not need to take custody of their voters’ assets at any point.

<p align="right">(<a href="#top">back to top</a>)</p>

### Built With

* [node.js](https://nodejs.org/en/)
* [python](https://www.python.org/)

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple example steps.

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/InfStones-com/Stacks-Pool-Manager.git
   ```
2. run install.sh
   ```sh
   cd Stacks-Pool-Manager
   ./install.sh
   ```

<p align="right">(<a href="#top">back to top</a>)</p>

### Configurations

1. Enter your information in `stacks/config/.env`
   ```js
    poolPrivateKey=<poolOperatorPrivateKey>
    poolSTXAddress=<poolOperatorSTXAddress>
    poolBTCAddress=<poolOperatorBTCAddress>
   ```

2. Enter your information in `stacks/config/fee.json`
   ```js
    {
        "preCharge": {
            "minimumCharge": "0.2 BTC",
            "maximumCharge": "0.5 BTC",
            "feeRate": {
                "item1": "10%",
                "item2": "2%"
            }
        },
        "poolCharge": {
            "poolRewardAddress": "nqpLw9Qu5tnboENHX8PHN2rNBUMYd7qiqoNSGnCG",
            "minimumVoterStackedSTX": "500",
            "flatFeeRate": "5%",
            "tierFeeRate": {
                "0": "15%",
                "100000": "10%",
                "200000": "7.5%",
                "300000": "6%"
            }
        }
    }
   ```
- `preCharge` is the charge that will be taken out from the total pool rewards before any voter can receive stacking reward. The `preCharge` guarantees payment to pool operator or special purposes, for instance, charity, fundraising, etc.
    - `minimumCharge` is the minimum amount reward in BTC that `preCharge` will take.
        - If `minimumCharge` is empty, `preCharge` will take the smaller amount between the sum of all charges associated with `feeRate` items and the `maximumCharge`.
        - In our example:
            > Given that the total pool rewards is greater than `0.2 BTC`. The pool operator is guaranteed a payout of `0.2 BTC`.
    - `maximumCharge` is the maximum amount reward in BTC that the `preCharge` will take.
        - If `maximumCharge` is empty, `preCharge` will take the larger amount between the sum of all charges associated with `feeRate` items and the `minimumCharge`.
        - In our example:
            > The pool operator will take a payout of `0.5 BTC` maximum, regardless of the total pool rewards.
    - `feeRate` is the portion of the rewards that will be subtracted from the total pool rewards. This percentage rate guarantees payment to the items listed.
        - `feeRate` items are customizable by pool operators, and can be used to set special operator fee or charity goal.
        - `feeRate` **cannot** be empty!
        - In our example:
            > `item1` and `item2` will take `10%` and `2%`, respectively, of total pool rewards. The remaining `88%` of total pool rewards will be divided between voters.
        - If pool operator do not want to take `preCharge`, they must set the `minimumCharge` as `0 BTC` and `feeRate` items with `0%`.
            ```
            "preCharge": {
                "minimumCharge": "0 BTC",
                "feeRate": {
                    "item1": "0%"
                }
            }
            ```
- `poolCharge` is the charge that will be taken by the pool operator. This is calculated using the difference of total pool rewards and `preCharge` amount.
    - `poolRewardAddress` is the address where the pool received rewards. The pool operator will be responsible to distribute those rewards to voters based on the fee schedule.
    - `minimumVoterStackedSTX` is the minimum STX amount that the voter needed to stack in order to receive their share of the total pool reward.
        - If `minimumVoterStackedSTX` is not provided or the value is empty as `""`, voters will receive their cycle reward regardless of the stacked amount.
        - In our example:
            > `minimumVoterStackedSTX` is set as 500 STX. If a voter stacked 499 STX, they will NOT receive their reward for that cycle.
    - `flatFeeRate` is flat percentage fee that is taken by the pool operator as operator fee from each voter.
        - If `flatFeeRate` is not provided or the value is empty as `""`, operator fee will be calculated using the `tierFeeRate`.
        - In our example:
            > A flat `5%` is taken from each voter's cycle reward as operator fee.
    - `tierFeeRate` calculates the percentage fee that is taken by the pool operator as operator fee from each voter based on the voter stacked amount.
        - If `tierFeeRate` is not provided or the value is empty as `""`, operator fee will be calculated using the `flatFeeRate`.
        - In our example:
            > If a voter stacks between `0` and `100000` STX, `15%` will be taken from their cycle reward as operator fee. Subsequently, if a voter stacks between `100001` and `200000`, `10%` will be taken from their cycle reward as operator fee, and etc..
    - Either `tierFeeRate` or `flatFeeRate` **must** be provided.
    - If `flatFeeRate` and `tierFeeRate` are both provided, `flatFeeRate` will be ignored.

3. Enter voters information in `stacks/voters/voters_cycleCommitted_<cycleNumber>.json`
    ```js
    [
        {
        "voterName": "Andy",
        "voterAddress": "STDWH8EPQAFBZRJXX2GRKD7EACAGPYIFFUXW2EC6",
        "cycleCommitted": 20,
        "lockingCycles": 3,
        "stackedSTX": "1000"
        },
        {
        "voterName": "Bob",
        "voterAddress": "STPKL5MUDHSQH89NQ8J4XTQF8MEDP7FJKNRHYGZX",
        "cycleCommitted": 20,
        "lockingCycles": 3,
        "stackedSTX": "1000"
        }
    ]
    ```
- `stacks/voters/` is the directory that contained the JSON files that have voters information.
- The voters information JSON naming structure is as `voters_cycleCommitted_<cycleNumber>.json`.
    - Where `<cycleNumber>` is the cycle that the voters will be committed. For example, if voters want their stack to be committed starting at cycle 20, the file will be named `voters_cycleCommitted_20.json`
- `voterName` is an easily identifiable name for the voter.
- `voterAddress` is the address voter used to stack their tokens. This is **required**.
- `cycleCommitted` is the starting cycle at which voter delegation will be committed. This is the same value as the `<cycleNumber>` from the file name. This is **required**.
- `lockingCycles` is the number of cycles the voter's tokens will be locked up, ranging from 1 to 12. This is **required**.
- `stackedSTX` is the amount of STX that the voter stacked. This is **required**.

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->
## Usage

### runPool

runPool will start stacking and committing periodically and takes the following arguments:
```
-v, --voters               Required. The local directory where the voters information is stored.
-f, --fee                  Required. The local JSON config file where the fee percentage is stored.
-a, --api                  Optional. The stacks API use to query data from the blockchain. Default is https://api.stacking-club.com.
-h, --help                 Show this help message and exit.
```

Start the runPool:
```
python3 Stacks-Pool-Manager/stacks/runPool.py -v Stacks-Pool-Manager/stacks/voters -f Stacks-Pool-Manager/stacks/config/fee.json
```

- ##### Stacking

    runPool will check every 4 hours for new voters for the next cycle and start stacking new voters if exist. This process may take a long time for large amount of voters since the number of transactions per block is limited.

    If there are new voters coming in after runPool has stacked for a cycle, and the new voters want to be stacked for the same cycle. Pool operator should edit the `voters_cycleCommitted_<cycleNumber>.json` and append the new voters to the file. runPool will automatically detects the new voters and stacks them for same cycle.

- ##### Commiting

    runPool will also check if it can commit for the next cycle every 4 hours. If the next cycle starts within 24 hours, it will start the commit process for the next cycle. Only one commit can be run per cycle so make sure that all voters have been stacked.

**NOTE:** Stacks nodes admit transactions in the mempool, but up to a limit ([25](https://github.com/blockstack/stacks-blockchain/blob/master/src/core/mempool.rs#L60) in the [current implementation](https://github.com/blockstack/stacks-blockchain/blob/master/src/core/mempool.rs#L60)). So limit any “chain” of unconfirmed transactions from a single address to **less than 25**. Making this limit higher has downsides, discussed in [this issue](https://github.com/blockstack/stacks-blockchain/issues/2384).

<p align="right">(<a href="#top">back to top</a>)</p>

### calculateMatching

calculateMatching will calculate the amount of STX the pool operator will commit to match delegated STX from voters.
. It takes the following arguments:
```
-r, --poolRewardAddress    Required. The pool reward address.
-p, --matchPercent         Required. The percent of delegated STX to stack in order to match delegated STX.
-t, --matchTokenMaximum    Optional. The maximum amount of token in STX to stack in order to match voters delegation.
-c, --cycle                Optional. The cycle number which to find the total STX delegated. Default is next cycle.
-a, --api                  Optional. The stacks API use to query data from the blockchain. Default is https://api.stacking-club.com.
-h, --help                 Show this help message and exit.
```

Start the calculateMatching:

- To match 50% of total stacked STX:
    ```
    python3 Stacks-Pool-Manager/stacks/calculateMatching.py -r gre9ryh3saSz5DrgGmV2o6tGQxxapKdR2r -p 50
    ```
    with result:
    ```
    Total delegation amount for cycle 21: 16000861.537158 STX
    Matching 8000430.768579 STX for cycle 21.
    ```

- To match 50% of total stacked STX, up to 50,000 STX:
    ```
    python3 Stacks-Pool-Manager/stacks/calculateMatching.py -r gre9ryh3saSz5DrgGmV2o6tGQxxapKdR2r -p 50 -t 50000
    ```
    with result:
    ```
    Total delegation amount for cycle 21: 16000861.537158 STX
    Matching 50000.0 STX for cycle 21.
    ```
**NOTE**: calculateMatching only calculates the amount of STX needed for matching voters stacked STX. Operators will need to delegate and stack using the calculated results.

<p align="right">(<a href="#top">back to top</a>)</p>

### calculateRewards

calculateRewards will calculate the rewards for voters of a pool, it takes the following arguments:
```
-f, --fee                  Required. The local JSON config file where the fee percentage is stored.
-a, --api                  Optional. The stacks API use to query data from the blockchain. Default is https://api.stacking-club.com.
-c, --cycle                Optional. The cycle number which to find the rewards. Default is most recent completed cycle.
-h, --help                 Show this help message and exit.
```

Start the calculateRewards:

- To calculate the rewards for the most recent completed cycle:
    ```
    python3 Stacks-Pool-Manager/stacks/calculateMatching.py -f Stacks-Pool-Manager/stacks/config/fee.json
    ```

- To calculate the rewards for a different completed cycle:
    ```
    python3 Stacks-Pool-Manager/stacks/calculateMatching.py -f Stacks-Pool-Manager/stacks/config/fee.json -c 20
    ```

A file `cycle<cycleNumber>Rewards.json` will be generated with all the rewards in BTC for `preCharge` and for each `voter`
```js
{
    "preCharge": {
        "feeRate": {
            "item1": "0.0175768470",
            "item2": "0.0035153694"
        }
    },
    "votersReward": {
        "ST1WSBT3NYWSMW0RR5191BPGZRVAG1BV7S0EH2401": "0.1452599574",
        "ST2W00J9JB0SWTPW949H4GYJHVK7QT49409JBN6KW": "0.0000263140",
        "ST8GN2BJ1DRYN4HYKE6A2BZNZ71C6BC5YGP8AXV7": "0.0000437402",
        "ST398VDZ344JH5MAB5N9TMDNCV47JS9VC61RAPV5H": "0.0000132666"
    },
    "forfeitedReward": {
        "STPN3YFCCZ71VGASMK145BK1BJBANT773YBH3NJ3": "0.0000154532",
        "ST2YMJ41FE2AW4A89F755Q32VE57GA2ZYA8NBJ7C7": "0.0000154532",
        "ST1TA2R5PWCVZW1JH8ZEECFG6MHQK2GTJN3P1FHSV": "0.0000154532"
    },
    "totalPoolReward": "0.1757684700",
    "totalPreCharge": "0.0210922164",
    "totalOperatorFee": "0.0092866158",
    "totalVotersReward": "0.1453432782",
    "totalForfeitedReward": "0.0000463596"
}
```
**NOTE**: Voters under `forfeitedReward` did not meet the `minimumVoterStackedSTX` requirement in the `fee.json`, and therefore their rewards are forfeited. The rewards calculation shown for `forfeitedReward` are calculated pre-operator fees.

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- CONTRIBUTING -->
## Contributing

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- CONTACT -->
## Contact

InfStones: [@infstones](https://twitter.com/infstones) - contact@infstones.com

Project Link: [https://github.com/InfStones-com/Stacks-Pool-Manager](https://github.com/InfStones-com/Stacks-Pool-Manager)

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [The MIT License](https://opensource.org/licenses/MIT)
* [Stacks](https://www.stacks.co/)

<p align="right">(<a href="#top">back to top</a>)</p>