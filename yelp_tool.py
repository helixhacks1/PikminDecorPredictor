

import requests
import json
import os.path
import pickle
from ratelimiter import RateLimiter
from decor_to_tag_mapping import yelp_decors_to_tags

class YelpTool:
    def __init__(self, api_key):
        self.api_key = api_key
        self.cache = 'caches/yelp_cache.pickle'
        self.dict = {}

    def predict_row(self, yelp_data, seedling_date, burger_shop_start_date):
        return self.__predict(yelp_data, seedling_date, burger_shop_start_date)

    def predict(self, longitude, latitude, radius, seedling_date, burger_shop_start_date, debug_mode=False):
        result = self.__query(longitude=longitude, latitude=latitude, radius=radius)
        if debug_mode:
            print(f"DEBUG: {result}")

        ret_dict = {}
        for element in result:
            # print(f"running on element {element['name']}")
            decors = self.__predict(element, seedling_date, burger_shop_start_date)
            if len(decors) > 0:
                ret_dict[element["name"]] = decors
        return ret_dict

    def __predict(self, yelp_data, seedling_date, burger_shop_start_date):
        decors = []
        if "categories" in yelp_data:
            categories = yelp_data["categories"]
            for decor_type, tag_list in yelp_decors_to_tags.items():
                if self.find_match(tag_list, categories):
                    decors.append(decor_type)
        return decors

    def find_match(self, list, yelp_categories):
        for tag in list:
            for category in yelp_categories:
                if "alias" in category:
                    if category["alias"] == tag:
                        return True
        return False

    def fill_in_data(self, data, location_tool, debug_mode=False):
        # initialize a dict to cache gps coords for locations
        if os.path.exists(self.cache):
            with open(self.cache, 'rb') as handle:
                # print(f"Loading yelp data from disk")
                self.dict = pickle.load(handle)
        else:
            print(f"No cache found, creating new yelp dictionary (This may take a while)...")
            self.dict = {}

        for index, row in data.iterrows():
            row_key = self.__create_row_key(row)
            if row_key not in self.dict:
                # get GPS location of row
                location = location_tool.lookup_location(row)

                if location:
                    if debug_mode:
                        print(f"running {row['Location']} through yelp.")

                    data_yelp = self.__query_location(location, self.__clean_decor_title(row["Location"]))
                else:
                    data_yelp = None

                if debug_mode and data_yelp is not None:
                    print(f"{data_yelp}")

                self.dict[row_key] = data_yelp
            else:
                # it exists, load from cache
                data_yelp = self.dict[row_key]

            if data_yelp:
                # print(f"found yelp match for {row_key}")
                data.loc[index, "Yelp Data"] = json.dumps(data_yelp)
            else:
                # print(f"NO MATCH found yelp match for {row_key}")
                data.loc[index, "Yelp Data"] = None

        with open(self.cache, 'wb') as handle:
            pickle.dump(self.dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

        return data

    @RateLimiter(max_calls=10, period=1)
    def __query(self, latitude, longitude, radius):
        url = f"https://api.yelp.com/v3/businesses/search"
        payload = {
            "latitude": f"{latitude}",
            "longitude": f"{longitude}",
            "radius": f"{radius}"
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        response = requests.request("GET", url, headers=headers, params=payload).json()
        if "businesses" in response:
            return response["businesses"]
        return None

    @RateLimiter(max_calls=10, period=1)
    def __query_location(self, location_osm, location_name):
        # Note that yelp doesn't support bounding boxes, so we instead convert the location
        # into a gps with a radius: https://www.yelp.com/developers/documentation/v3/business_search
        latitude = location_osm.latitude
        longitude = location_osm.longitude
        radius = 40000

        url = f"https://api.yelp.com/v3/businesses/search"
        payload = {
            "term" : f"{location_name}",
            "latitude" : f"{latitude}",
            "longitude" : f"{longitude}",
            "radius" : f"{radius}"
        }
        headers = {
            "Authorization" : f"Bearer {self.api_key}"
        }
        response = requests.request("GET", url, headers=headers, params=payload).json()

        if "businesses" in response:
            for result in response["businesses"]:
                if "name" in result:
                    if location_name in result["name"]:
                        return result
        return None

    def __clean_decor_title(self, title):
        if title.startswith("Near "):
            return title[5:]
        elif title.startswith("near "):
            return title[5:]
        else:
            return title

    def __create_row_key(self, row):
        country = row["Country"]
        state = row["State"]
        suburb = row["Suburb"]
        location = row["Location"]
        return f"{suburb}, {state}, {country}, {location}"