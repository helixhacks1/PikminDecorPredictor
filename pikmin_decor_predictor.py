from osm_tool import OSMTool
from location_tool import LocationTool
from foursquare_tool import FoursquareTool
from google_places_tool import GooglePlacesTool
from yelp_tool import YelpTool
from decor_type import DecorType
from dataset import Dataset

from datetime import datetime
import json
import pandas as pd

class PikminDecorPredictor:
    def __init__(self, osm_email=None, foursquare_key=None, google_places_key=None, yelp_key=None):
        self.foursquare_key = foursquare_key
        self.google_places_key = google_places_key
        self.yelp_key = yelp_key
        self.osm_email = osm_email

        if osm_email:
            self.location_tool = LocationTool(osm_email)
        self.osm_tool = OSMTool()
        if self.foursquare_enabled():
            self.foursquare_tool = FoursquareTool(self.foursquare_key)
        if self.google_places_enabled():
            self.google_places_tool = GooglePlacesTool(self.google_places_key)
        if self.yelp_enabled():
            self.yelp_tool = YelpTool(self.yelp_key)

    def fill_in_data(self, data, debug_mode=False):
        print("Starting to fill in data, this my take a while...")
        # do a pass through the dataset and convert the suburb, city, country fields to a GPS coordinate.
        self.location_tool.make_location_dict(data)

        # do another pass through the dataset and fill in OSM data, if it can be found.
        data = self.osm_tool.fill_in_data(data, self.location_tool)
        # if the foursquare credentials are defined, do another pass through the
        # dataset and fill in foursquare data, if it can be found.
        if self.foursquare_enabled():
            data = self.foursquare_tool.fill_in_data(data, self.location_tool, debug_mode=debug_mode)
        if self.google_places_enabled():
            data = self.google_places_tool.fill_in_data(data, self.location_tool, debug_mode=debug_mode)
        if self.yelp_enabled():
            data = self.yelp_tool.fill_in_data(data, self.location_tool, debug_mode=debug_mode)
        return data

    def predict_row(self, row, truth):
        osm_data = row["OSM Data"]
        foursquare_data = row["Foursquare Data"]
        google_places_data = row["Google Places Data"]
        yelp_data = row["Yelp Data"]

        # convert date to integer
        seedling_date = datetime.strptime(row["Date"], '%m/%d/%Y').timestamp()
        # convert the date that burger_shop went live to an integer
        burger_shop_start_date = datetime.strptime("12/18/2021", '%m/%d/%Y').timestamp()

        decors = []
        if not osm_data and not foursquare_data and not google_places_data and not yelp_data:
            return []

        if osm_data:
            decors.extend(self.osm_tool.predict_row(osm_data, seedling_date, burger_shop_start_date))
        if foursquare_data and self.foursquare_enabled():
            decors.extend(self.foursquare_tool.predict_row(json.loads(foursquare_data),
                                                           seedling_date,
                                                           burger_shop_start_date))
        if google_places_data and self.google_places_enabled():
            decors.extend(self.google_places_tool.predict_row(json.loads(google_places_data),
                                                              seedling_date,
                                                              burger_shop_start_date))
        if yelp_data and self.yelp_enabled():
            decors.extend(self.yelp_tool.predict_row(json.loads(yelp_data),
                                                     seedling_date,
                                                     burger_shop_start_date))
        if len(decors) > 0:
            return decors
        else:
            return []

    def predict(self, longitude, latitude, radius, date, debug_mode):
        # convert date to integer
        if not date:
            seedling_date = datetime.now().timestamp()
        else:
            seedling_date = datetime.strptime(date, '%m/%d/%Y').timestamp()

        # convert the date that burger_shop went live to an integer
        burger_shop_start_date = datetime.strptime("12/18/2021", '%m/%d/%Y').timestamp()

        print(f"\nOSM Results:")
        self.pretty_print_dict(self.osm_tool.predict(longitude=longitude,
                                                     latitude=latitude,
                                                     radius=radius,
                                                     seedling_date=seedling_date,
                                                     burger_shop_start_date=burger_shop_start_date,
                                                     debug_mode=debug_mode))
        print(f"==========================")
        if self.foursquare_enabled():
            print(f"\nFoursquare Results:")
            self.pretty_print_dict(self.foursquare_tool.predict(longitude=longitude,
                                                                latitude=latitude,
                                                                radius=radius,
                                                                seedling_date=seedling_date,
                                                                burger_shop_start_date=burger_shop_start_date,
                                                                debug_mode=debug_mode))
            print(f"==========================")
        if self.google_places_enabled():
            print(f"\nGoogle Places Results:")
            self.pretty_print_dict(self.google_places_tool.predict(longitude=longitude,
                                                                   latitude=latitude,
                                                                   radius=radius,
                                                                   seedling_date=seedling_date,
                                                                   burger_shop_start_date=burger_shop_start_date,
                                                                   debug_mode=debug_mode))
            print(f"==========================")
        if self.yelp_enabled():
            print(f"\nYelp Results:")
            self.pretty_print_dict(self.yelp_tool.predict(longitude=longitude,
                                                          latitude=latitude,
                                                          radius=radius,
                                                          seedling_date=seedling_date,
                                                          burger_shop_start_date=burger_shop_start_date,
                                                          debug_mode=debug_mode))
            print(f"==========================")

    def predict_dataset(self, data, truth, debug_mode=False):
        # initialize list for predictions output
        decor_predictions = []
        usage_dict = {Dataset.osm: {},
                      Dataset.foursquare: {},
                      Dataset.google_places: {},
                      Dataset.yelp: {}}
        for index, row in data.iterrows():
            # predict row
            prediction_for_row = self.predict_row(row, truth[index])
            if len(prediction_for_row) > 0:
                prediction_index = 0
                x = 0
                for prediction in prediction_for_row:
                    if prediction.get_decor() == truth[index]:
                        prediction_index = x
                        # store which tag is used
                        keys = usage_dict[prediction.get_dataset()].keys()
                        print(f"{prediction.get_dataset()} == {type(prediction.get_label())}")
                        if prediction.get_label() in keys:
                            usage_dict[prediction.get_dataset()][prediction.get_label()] = \
                                usage_dict[prediction.get_dataset()][prediction.get_label()] + 1
                        else:
                            usage_dict[prediction.get_dataset()][prediction.get_label()] = 1
                    x = x + 1
                decor_predictions.append(prediction_for_row[prediction_index].get_decor())
            else:
                if debug_mode and len(prediction_for_row) == 0 and truth[index] != DecorType.roadside:
                    print("FAILED")
                    print("----------------------------")
                    print(f" {truth[index]} failed for {row['Location']}")
                    if row["OSM Data"] is not None:
                        print(f"OSM: {row['OSM Data'].tags()}")
                    if row["Foursquare Data"] is not None:
                        print(f"Foursquare: {row['Foursquare Data']}")
                    if row["Google Places Data"] is not None:
                        print(f"Google Places: {row['Google Places Data']}")
                    if row["Yelp Data"] is not None:
                        print(f"Yelp: {row['Yelp Data']}")
                    print("----------------------------")
                decor_predictions.append(DecorType.roadside)
        self.print_tag_usage(usage_dict)
        return pd.DataFrame(decor_predictions, columns=['Decor'])

    def pretty_print_dict(self, dict):
        for key, value in dict.items():
            decors = [x.value for x in value]
            print(f"{key}: {decors}")

    def print_tag_usage(self, usage_dict):
        for key, dict in usage_dict.items():
            i = 0
            print('==================')
            print(f"{key}")
            print('==================')
            for decor, count in dict.items():
                i = i + count
                print(f"{decor}: {count}")
            print("---------")
            print(f"Total hits: {i}")
            print("---------")

    def foursquare_enabled(self):
        return self.foursquare_key is not None

    def google_places_enabled(self):
        return self.google_places_key is not None

    def yelp_enabled(self):
        return self.yelp_key is not None
