#!/usr/bin/env python3

from pikmin_decor_predictor import PikminDecorPredictor
import argparse

def cli_to_args():
    """
    converts the command line interface to a series of args
    """
    cli = argparse.ArgumentParser(description="Script that takes a latitude and longitude as required inputs, "
                                              "and attempts to output potential Pikmin Bloom decors at that location."
                                              "Optionally, a radius and a date may be given to narrow down results. "
                                              "Also, API keys from developer accounts must be given to query data "
                                              "sources such as Foursquare and Yelp.")
    cli.add_argument('-latitude',
                     type=range_limited_latitude_type,
                     default=None,
                     required=True,
                     help='Latitude for where to look for decors. Must be a value between -90.0 and 90.0')
    cli.add_argument('-longitude',
                     type=range_limited_longitude_type,
                     default=None,
                     required=True,
                     help='Longitude for where to look for decors. Must be a value between -180.0 and 180.')
    cli.add_argument('-radius',
                     type=int, default=150,
                     help='Radius for how far to predict the decors. Given in meters, each dataset has its own rules as '
                          'to how large this radius can be.')
    cli.add_argument('-date',
                     type=int, default=None,
                     help='Date formatted as m/d/Y, IE 12/18/2021.')

    cli.add_argument('-foursquare_api_key',
                     type=str, default=None,
                     help='Required to enable foursquare data. Requires a Foursquare developer account to generate. \
                     Without this option, foursquare is skipped')
    cli.add_argument('-google_places_api_key',
                     type=str, default=None,
                     help='Required to enable Google Places data. Requires a Google Places developer account to generate. \
                     Without this option, Google Places is skipped')
    cli.add_argument('-yelp_api_key',
                     type=str, default=None,
                     help='Required to enable Yelp data. Requires a Yelp developer account to generate. \
                     Without this option, Yelp is skipped')

    cli.add_argument('-debug',
                     default=False, action="store_true",
                     help='Add this flag to print extra debug info.')
    return cli.parse_args()


def range_limited_longitude_type(arg):
    min_val = -180.0
    max_val = 180.0
    try:
        f = float(arg)
    except ValueError:
        raise argparse.ArgumentTypeError("Must be a floating point number")
    if f < min_val or f > max_val:
        raise argparse.ArgumentTypeError("Argument must be <= " + str(max_val) + " and >= " + str(min_val))
    return f


def range_limited_latitude_type(arg):
    min_val = -90.0
    max_val = 90.0
    try:
        f = float(arg)
    except ValueError:
        raise argparse.ArgumentTypeError("Must be a floating point number")
    if f < min_val or f > max_val:
        raise argparse.ArgumentTypeError("Argument must be <= " + str(max_val) + " and >= " + str(min_val))
    return f


if __name__ == '__main__':
    args = cli_to_args()

    decor_predictor = PikminDecorPredictor(foursquare_key=args.foursquare_api_key,
                                           google_places_key=args.google_places_api_key,
                                           yelp_key=args.yelp_api_key)

    print(f"Predicting Latitude:{args.latitude} Longitude:{args.longitude} Radius:{args.radius}m")
    decor_predictor.predict(latitude=args.latitude,
                            longitude=args.longitude,
                            radius=args.radius,
                            date=args.date,
                            debug_mode=args.debug)

