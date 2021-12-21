import sys
import json
import requests
import argparse
import subprocess
from subprocess import Popen, PIPE

formatter = lambda prog: argparse.HelpFormatter(prog, max_help_position=200)
parser = argparse.ArgumentParser(description = "Match the delegated STX.", formatter_class=formatter, add_help=False)

# Options for matchSTX
parser.add_argument("-r", "--poolRewardAddress", help = "Required. The pool reward address.", required = True, metavar='')
parser.add_argument("-p", "--matchPercent", help = "Required. The percent of delegated STX to stack in order to match delegated STX.", type = float, required = True, metavar = '')
parser.add_argument("-t", "--matchTokenMaximum", help = "Optional. The maximum amount of token in STX to stack in order to match voters delegation.", type = float, required = False, metavar = '')
parser.add_argument("-c", "--cycle", help = "Optional. The cycle number which to find the total STX delegated. Default is next cycle.", type = int, required = False, metavar='')
parser.add_argument("-a", "--api", help = "Optional. The stacks API use to query data from the block chain. Default is https://api.stacking-club.com.", required = False, default = "https://api.stacking-club.com", metavar='')
parser.add_argument("-h", "--help", action = "help", help = "Show this help message and exit.")

if len(sys.argv) == 1:
    parser.print_help()
    parser.exit()

args = parser.parse_args()

# Sanity check
if args.cycle is None:
    currentCycleInfo = requests.get(f"{args.api}/api/meta-info")
    cycle = currentCycleInfo.json()[0]["pox"]["current_cycle"]["id"] + 1
else:
    cycle = args.cycle

def checkSTX():
    operatorRewardCycleInfo = requests.get(f"{args.api}/api/stacker-data?variables={args.poolRewardAddress}____{cycle}")
    totalStackedMicroSTX = operatorRewardCycleInfo.json()["stackingTxs"]["aggregate"]["sum"]["amount"]
    if totalStackedMicroSTX is None:
        parser.error(f"The address {args.poolRewardAddress} does not exist!")
    totalStackedSTX = totalStackedMicroSTX/1000000
    print(f"Total delegation amount for cycle {cycle}: {totalStackedSTX} STX")
    return totalStackedSTX


def matchSTX():
    matchAmount = 0
    totalStackedSTX = checkSTX()
    if args.matchPercent is not None:
        matchAmount = totalStackedSTX * (args.matchPercent / 100)
    if args.matchTokenMaximum is not None:
        matchTokenMaximum = args.matchTokenMaximum
        if matchAmount > matchTokenMaximum:
            matchAmount = matchTokenMaximum

    if matchAmount > totalStackedSTX:
        matchAmount = totalStackedSTX

    print(f"Matching {matchAmount} STX for cycle {cycle}.")



if __name__ == "__main__":
    matchSTX()

