import os
import re
import sys
import json
import argparse
import requests
from datetime import datetime, date

formatter = lambda prog: argparse.HelpFormatter(prog, max_help_position=200)
parser = argparse.ArgumentParser(description='Calculate rewards of given STX Address.', formatter_class=formatter, add_help=False)
parser.add_argument("-f", "--fee", help = "Required. The local JSON config file where the fee percentage is stored.", required = True, metavar='')
parser.add_argument("-a", "--api", help = "Optional. The stacks API use to query data from the block chain. Default is https://api.stacking-club.com.", required = False, default = "https://api.stacking-club.com", metavar='')
parser.add_argument("-c", "--cycle", help = "Optional. The cycle number which to find the rewards. Default is most recent completed cycle.", type = int, required = False, metavar='')
parser.add_argument("-h", "--help", action = "help", help = "Show this help message and exit.")

if len(sys.argv) == 1:
    parser.print_help()
    parser.exit()

args = parser.parse_args()

if args.cycle is None:
    currentCycleInfo = requests.get(f"{args.api}/api/meta-info")
    currentCycle = currentCycleInfo.json()[0]["pox"]["current_cycle"]["id"]
    rewardCycle = currentCycle - 1
else:
    rewardCycle = args.cycle

# Sanity check
def sanityCheck():
    if not os.path.isfile(args.fee):
        parser.error(f"The file {args.fee} does not exist!")

    rewardCycleInfo = requests.get(f"{args.api}/api/cycle-info?cycle={rewardCycle}")
    rewardCycleStartDateEpoch = datetime.fromtimestamp(rewardCycleInfo.json()["startDate"] / 1000)
    rewardCycleEndDateEpoch = datetime.fromtimestamp(rewardCycleInfo.json()["endDate"] / 1000)

    dateFormat = '%Y-%m-%d %H:%M:%S'
    rewardCycleStartDate = datetime.strptime(rewardCycleStartDateEpoch.strftime(dateFormat), dateFormat)
    currentDate= datetime.strptime(date.today().strftime(dateFormat), dateFormat)
    rewardCycleEndDate = datetime.strptime(rewardCycleEndDateEpoch.strftime(dateFormat), dateFormat)

    if currentDate <= rewardCycleStartDate:
        print(f"Cycle {rewardCycle} has not start, please try again when cycle starts on {rewardCycleStartDate}.")
        exit()
    elif currentDate <= rewardCycleEndDate:
        print(f"Cycle {rewardCycle} has not finish, please try again when cycle finishes on {rewardCycleEndDate}.")
        exit()

# Open input file
with open(args.fee) as jsonFile:
    fee = json.load(jsonFile)
    minimumCharge = float(re.findall(r"[+-]? *(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", fee.get("preCharge",{}).get("minimumCharge", '0 BTC') or '0 BTC')[0])
    maximumCharge = float(re.findall(r"[+-]? *(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", fee.get("preCharge",{}).get("maximumCharge", '0 BTC') or '0 BTC')[0])
    feeRate = fee.get("preCharge",{}).get("feeRate", {})
    poolRewardAddress = fee.get("poolCharge", {}).get("poolRewardAddress")
    minimumVoterStackedSTX = float(fee.get("poolCharge", {}).get("minimumVoterStackedSTX") or 0)
    flatFeeRate = fee.get("poolCharge", {}).get("flatFeeRate")
    tierFeeRate = fee.get("poolCharge", {}).get("tierFeeRate")

# Collect cycle data
operatorRewardCycleInfo = requests.get(f"{args.api}/api/stacker-data?variables={poolRewardAddress}____{rewardCycle}")
totalStackedMicroSTX = operatorRewardCycleInfo.json()["stackingTxs"]["aggregate"]["sum"]["amount"]

if totalStackedMicroSTX is None:
    parser.error(f"The address {poolRewardAddress} does not exist!")

totalPoolReward = operatorRewardCycleInfo.json()["blockRewards"]["aggregate"]["sum"]["reward_amount"]/100000000
totalStackedSTX = operatorRewardCycleInfo.json()["stackingTxs"]["aggregate"]["sum"]["amount"]/1000000
voters = operatorRewardCycleInfo.json()["stackingTxs"]["nodes"]

def verifyFeeConfig():
    if minimumCharge and maximumCharge:
        if minimumCharge > maximumCharge:
            print(f"[ERROR]: minimumCharge cannot be greater than maximumCharge in fee.")
            exit()

    if feeRate:
        totalFeeRatePercent = 0
        for item in feeRate:
            itemFeePercent = float(feeRate[item].rstrip("%"))
            totalFeeRatePercent += itemFeePercent
        if totalFeeRatePercent > 100:
            print(f"[ERROR]: Total feeRate is more than 100% in fee.")
            exit()
    else:
        print(f"[ERROR]: feeRate cannot be empty.")
        exit()

    if tierFeeRate:
        if not all(tierFeeRate.values()):
            print(f"[ERROR]: tierFeeRate value cannot be empty in fee.")
            exit()

    if not flatFeeRate and not tierFeeRate:
        print(f"[ERROR]: Both flatFeeRate and tierFeeRate are empty in fee.")
        exit()


def calculatePreCharge(totalPoolReward):
    totalPreCharge = 0
    totalFeeRatePercent = 0
    if feeRate:
        for item in feeRate:
            itemFeePercent = float(feeRate[item].rstrip("%"))
            itemFee = totalPoolReward*(itemFeePercent / 100)
            totalPreCharge += itemFee
            totalFeeRatePercent += itemFeePercent
            rewardsJson["preCharge"]["feeRate"][item] = f"{itemFee:.10f}"

    if minimumCharge and totalPoolReward <= minimumCharge:
        print(f"Total pool reward for cycle {rewardCycle}: {totalPoolReward} BTC. Minimum charge is {minimumCharge} BTC. Withdrawing {totalPoolReward} BTC.")
        totalPreCharge = totalPoolReward
        # recalculate the feeRate rewards
        updateFeeRate(totalFeeRatePercent, totalPoolReward)

    if minimumCharge and totalPoolReward != totalPreCharge and totalPreCharge <= minimumCharge:
        print(f"Total pool reward for cycle {rewardCycle}: {totalPoolReward} BTC. Minimum charge is {minimumCharge} BTC. Total pre charge is {totalPreCharge:.10f}. Withdrawing {minimumCharge} BTC.")
        totalPreCharge = minimumCharge
        # recalculate the feeRate rewards
        updateFeeRate(totalFeeRatePercent, minimumCharge)

    if maximumCharge and totalPreCharge > maximumCharge:
        print(f"Total pool reward for cycle {rewardCycle}: {totalPoolReward} BTC. Maximum charge is {maximumCharge} BTC. Total pre charge is {totalPreCharge:.10f}. Withdrawing {maximumCharge} BTC.")
        totalPreCharge = maximumCharge
        # recalculate the feeRate rewards
        updateFeeRate(totalFeeRatePercent, maximumCharge)

    rewardsJson["totalPoolReward"] = f"{totalPoolReward:.10f}"
    rewardsJson["totalPreCharge"] = f"{totalPreCharge:.10f}"
    return totalPreCharge


def calculateRewards(poolRewardAfterPreCharge):
    totalOperatorFee = 0
    totalForfeitedReward = 0
    totalVotersReward = 0

    for voter in voters:
        feePercent = None
        voterAddress = voter['stx_address']
        isDelegator = voter['is_delegator']
        if isDelegator:
            voterStackedSTX = voter['amount']/1000000
            # Calculate address rewards before fees
            rewardsBeforeFees = voterStackedSTX/totalStackedSTX * poolRewardAfterPreCharge
            if minimumVoterStackedSTX and minimumVoterStackedSTX > voterStackedSTX:
                rewardsJson["forfeitedReward"][voterAddress] = f"{rewardsBeforeFees:.10f}"
                totalForfeitedReward += rewardsBeforeFees
                continue

            # Calculate address fees
            if flatFeeRate:
                feePercent = flatFeeRate
            if tierFeeRate:
                feeTiers = list(tierFeeRate.keys())
                feeTiers.sort(reverse = True)
                for tier in feeTiers:
                    if voterStackedSTX >= int(tier):
                        feePercent = tierFeeRate[tier]
                        break
            feePercent = float(feePercent.rstrip("%"))

            poolOperatorFee = rewardsBeforeFees*(feePercent / 100)
            voterReward = rewardsBeforeFees - poolOperatorFee
            totalOperatorFee += poolOperatorFee
            totalVotersReward += voterReward
            rewardsJson["votersReward"][voterAddress] = f"{voterReward:.10f}"

    rewardsJson["totalOperatorFee"] = f"{totalOperatorFee:.10f}"
    rewardsJson["totalVotersReward"] = f"{totalVotersReward:.10f}"
    rewardsJson["totalForfeitedReward"] = f"{totalForfeitedReward:.10f}"
    with open(f"cycle{rewardCycle}Rewards.json", "w") as outfile:
        json.dump(rewardsJson, outfile, indent = 4)
    print(f"Calculated rewards for cycle {rewardCycle}.")


def updateFeeRate(totalFeeRatePercent, totalCharge):
    if feeRate:
        for item in feeRate:
            itemFeePercent = float(feeRate[item].rstrip("%"))
            itemFee = totalCharge*(itemFeePercent / 100) / (totalFeeRatePercent/100)
            rewardsJson["preCharge"]["feeRate"][item] = f"{itemFee:.10f}"


if __name__ == "__main__":
    rewardsJson = {
        "preCharge": {
            "feeRate": {}
        },
        "votersReward": {},
        "forfeitedReward": {}
    }
    sanityCheck()
    verifyFeeConfig()
    totalPreCharge = calculatePreCharge(totalPoolReward)
    totalPoolRewardAfterPreCharge = totalPoolReward - totalPreCharge
    calculateRewards(totalPoolRewardAfterPreCharge)

