import argparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="BTScreenshotAutomation")
    parser.add_argument(
        "-a", "--account", help="The name of the account", type=str, required=True)
    parser.add_argument(
        "-c", "--additionalCharts", nargs="+", help="The name of the additional charts")
    parser.add_argument(
        "-d", "--directory", help="The directory to save the chart screenshots", type=str, default=".")
    parser.add_argument(
        "-v", "--verbose", help="Display debug message", action="store_true")
    args = parser.parse_args()
    additionalCharts = set()
    if args.additionalCharts is not None:
        additionalCharts = set(args.additionalCharts)
    btSeedingAccount = BTSeeding.BTSeedingAccount(
        args.account, additionalCharts)
    btSeedingAccount.run(saveDir=args.directory)
