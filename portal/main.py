import argparse
import logging
import Portal
import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog="Dynatrace Synthetic Screenshot Automation")
    parser.add_argument(
        "-u", "--username", help="The username for the account", type=str, required=True)
    parser.add_argument(
        "-p", "--password", help="The password for the account", type=str, required=True)
    parser.add_argument(
        "-d", "--directory", help="The directory to save the chart screenshots", type=str, default=".")
    parser.add_argument(
        "-v", "--verbose", help="Display debug message", action="store_true")
    parser.add_argument(
        "-c", "--chart-names", nargs="+", help="The name of the chart to capture")
    args = parser.parse_args()
    portal = Portal.DynatracePortal(args.username, args.password)
    portal.login()
    for chart in tqdm.tqdm(args.chart_names):
        portal.saveChartToScreenshot(
            chartName=chart, cropChart=True, saveDir=args.directory)
        tqdm.tqdm.write("Finished saving image: \"{chartName}\" screenshot to {directory} directory".format(
            chartName=chart, directory=args.directory))
