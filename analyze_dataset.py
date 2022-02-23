#!/usr/bin/env python3

from data_tool import DataTool
from pikmin_decor_predictor import PikminDecorPredictor
import argparse

def cli_to_args():
    """
    converts the command line interface to a series of args
    """
    cli = argparse.ArgumentParser(description="Command Line Tool for loading a dataset based on the Pikmin Bloom" 
                                              " Decor Database, running its data through various data sources "
                                              "(IE, OpenStreetMap, Foursquare, etc.) and analyzing the "
                                              "accuracy of tags. The point of this script is to try to nail down which"
                                              "tags from which data sources are used to make decor Pikmin spawn.")
    cli.add_argument('-input_file',
                     type=str, default=None,
                     help='Input file, a CSV that contains pikmin decors. Either this, or pull_latest_data is required')
    cli.add_argument('-pull_latest_data',
                     default=False, action="store_true",
                     help='Pulls latest data instead of using an input file. Either this, or input_file is required.')
    cli.add_argument('-output_file',
                     type=str, default='output/output.csv',
                     help='Output file, a CSV that stores the predictions from data sources like OSM.')

    cli.add_argument('-email',
                     type=str,
                     help='Email for Nominatim, required to convert location data to GPS.')
    cli.add_argument('-foursquare_api_key',  
                     type=str, default=None,
                     help='Required to enable foursquare data. Requires a Foursquare developer account to generate. \
                     Without this option, foursquare is skipped')
    cli.add_argument('-google_places_api_key',
                     type=str, default=None,
                     help='Required to enable Google Places data. Requires a Google developer account to generate. \
                     Without this option, Google Places is skipped')
    cli.add_argument('-yelp_api_key',
                     type=str, default=None,
                     help='Required to enable Yelp data. Requires a Yelp developer account to generate. \
                     Without this option, Yelp is skipped')

    cli.add_argument('-invalidate_caches',
                     default=False, action="store_true",
                     help='Add this flag to invalidate caches and run predictions from scratch.')
    cli.add_argument('-debug',
                     default=False, action="store_true",
                     help='Add this flag to print extra debug info.')
    return cli.parse_args()


def validate_args(args):
    if args.input_file or args.pull_latest_data:
        print(f"Running on a dataset...")
        return
    else:
        raise Exception(f"Invalid CLI arguments. Either provide an input_file and an email to run on an entire dataset,"
                        f"or a longitude and latiude to predict on a given location.")


if __name__ == '__main__':
    args = cli_to_args()

    decor_predictor = PikminDecorPredictor(osm_email=args.email,
                                           foursquare_key=args.foursquare_api_key,
                                           google_places_key=args.google_places_api_key,
                                           yelp_key=args.yelp_api_key)

    data_tool = DataTool()
    data_tool.generate_directories()

    # remove caches, if requested. You should only do this if you think somethings wrong with your caches,
    # as most of these APIs only allow _x_ calls per day, and rerunning calls each time the script runs
    # would push you over their thresholds.
    if args.invalidate_caches:
        print("WARNING: Removing all caches for foursquare, yelp, osm locations, and google places.")
        data_tool.invalidate_caches()

    if args.pull_latest_data:
        data = data_tool.pull_latest_data()
    else:
        data = data_tool.load_csv(args.input_file)
    if data is None:
        raise Exception("Invalid path to input data, check if your input file exists.")

    # this uses OSM to convert the suburb, city, country fields to an OSM Location, then this location is used
    # to query whatever datasets are enabled.
    data = decor_predictor.fill_in_data(data, debug_mode=args.debug)

    # save the dataframe to file
    data_tool.output_to_file(data, args.output_file)

    # prepare the data for running predictions on it. This includes splitting the dataset,
    # and removing rows based on the dataset rule.
    decors_ground_truth, data = data_tool.prepare_dataset_for_predictions(data)

    # run through the data points and create a prediction for each, output as a dataframe
    predictions = decor_predictor.predict_dataset(data, decors_ground_truth, debug_mode=args.debug)

    data_tool.analyze_data(data, predictions, decors_ground_truth)

