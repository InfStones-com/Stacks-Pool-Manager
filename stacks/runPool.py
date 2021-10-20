import os
import sys
import json
import time
import platform
import requests
import argparse
import subprocess
from subprocess import Popen, PIPE

formatter = lambda prog: argparse.HelpFormatter(prog, max_help_position=200)
parser = argparse.ArgumentParser(description="Start delegate stack and commit.", formatter_class=formatter, add_help=False)

parser.add_argument("-v", "--voters", help = "Required. The local directory where the voters information is stored.", required = True, metavar='')
parser.add_argument("-f", "--fee", help = "Required. The local JSON config file where the fee percentage is stored.", required = True, metavar='')
parser.add_argument("-a", "--api", help = "Optional. The stacks API use to query data from the block chain. Default is https://api.stacking-club.com.", required = False, default = "https://api.stacking-club.com", metavar='')
parser.add_argument("-h", "--help", action = "help", help = "Show this help message and exit.")

if len(sys.argv)==1:
    parser.print_help()
    parser.exit()

args = parser.parse_args()

FILEPATH = os.path.dirname(os.path.abspath(__file__))
stackSTX_func = os.path.abspath(os.path.join(FILEPATH, "utils", "stackSTX.js"))
commitStacking_func = os.path.abspath(os.path.join(FILEPATH, "utils", "commitStacking.js"))


def sanityCheck():
    if not os.path.isfile(args.fee):
        parser.error(f"[ERROR]: The file: {args.fee} do not exist!")
    if not os.path.isdir(args.voters):
        parser.error(f"The path {args.voters} does not exist!")

def getCycleInfo():
    metaInfo = requests.get(f"{args.api}/api/meta-info")
    nextCycle = metaInfo.json()[0]["pox"]["next_cycle"]["id"]
    nextCycleInfo = requests.get(f"{args.api}/api/cycle-info?cycle={nextCycle}")
    cycleStartDateEpoch = int(nextCycleInfo.json()["startDate"] / 1000)
    minimumRequiredSTX= nextCycleInfo.json()["minimumThreshold"]
    currentDateEpoch= int(time.time())
    hoursUntilNextCycle = max((cycleStartDateEpoch - currentDateEpoch) / 3600, 0)
    cycleInfo = {
        "nextCycle": nextCycle,
        "hoursUntilNextCycle": hoursUntilNextCycle,
        "minimumRequiredSTX": minimumRequiredSTX
    }
    return cycleInfo


def runStackAndCommit():
    with open(args.fee) as jsonFile:
        fee = json.load(jsonFile)
    poolRewardAddress = fee.get("poolCharge", {}).get("poolRewardAddress")
    existingVoters = None
    committedCycle = 0

    while True:
        # stack delegated STX
        cycleInfo = getCycleInfo()
        nextCycle = cycleInfo["nextCycle"]
        hoursUntilNextCycle = cycleInfo["hoursUntilNextCycle"]
        minimumRequiredSTX = cycleInfo["minimumRequiredSTX"]
        votersFile = os.path.abspath(os.path.join(args.voters, f"voters_cycleCommitted_{nextCycle}.json"))
        voters = None

        if not os.path.isfile(votersFile):
            print(f"[WARN]: No voters information for cycle {nextCycle}.")
        else:
            with open(votersFile) as jsonFile:
                voters = json.load(jsonFile)

        if voters:
            newVoters = []
            for voter in voters:
                if existingVoters is None or voter not in existingVoters:
                    newVoters.append(voter)
            if newVoters and committedCycle < nextCycle:
                print(f"There are new voters. Start stacking delegated STX for upcoming cycle {nextCycle}. This will take some time...")
                p = subprocess.Popen(["node", stackSTX_func, json.dumps(newVoters)], universal_newlines=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                output, err = p.communicate()
                print(output)
            existingVoters = voters

        # sleep for 4 hours to wait for new stack to be in anchor block
        print("Sleeping for 4 hours...")
        time.sleep(14400)

        # commit delegated STX
        nextCycleInfo = requests.get(f"{args.api}/api/stacker-data?variables={poolRewardAddress}____{nextCycle}")
        stackedSTX = nextCycleInfo.json()["stackingTxs"]["aggregate"]["sum"]["amount"]/1000000

        if hoursUntilNextCycle <= 24:
            # Check if the delegated amount is enough
            if stackedSTX < minimumRequiredSTX:
                print(f"[ERROR]: Not enough stacked STX to commit. {stackedSTX}/{minimumRequiredSTX} STX.")
            else:
                print(f"Cycle {nextCycle} starts in {int(hoursUntilNextCycle)} hours.")
                if committedCycle < nextCycle:
                    print(f"Cycle {nextCycle} starts in {int(hoursUntilNextCycle)} hours. Confirming participation.")
                    p = subprocess.call(["node", commitStacking_func])
                    committedCycle = nextCycle
                    print("[END]: Committed to stacking...")


if __name__ == "__main__":
    sanityCheck()
    runStackAndCommit()

