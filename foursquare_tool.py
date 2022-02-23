
import requests
import urllib.parse
import json
import os.path
import pickle
from decor_to_tag_mapping import foursquare_decors_to_tags
from ratelimiter import RateLimiter


class FoursquareTool:
    def __init__(self, api_key):
        self.api_key = api_key
        self.foursquare_cache = 'caches/foursquare_cache.pickle'
        self.foursquare_dict = {}

    def __predict(self, element, seedling_date, burger_shop_start_date):
        decors = []
        if "categories" in element:
            for category in element["categories"]:
                if "name" in category:
                    category_name = category["name"]
                    for decor_type, tag_list in foursquare_decors_to_tags.items():
                        if category_name in tag_list:
                            decors.append(decor_type)
        return list(set(decors))

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

    def predict_row(self, foursquare_data, seedling_date, burger_shop_start_date):
        return self.__predict(foursquare_data, seedling_date, burger_shop_start_date)

    def fill_in_data(self, data, location_tool, debug_mode=False):
        # initialize a dict to cache gps coords for locations
        if os.path.exists(self.foursquare_cache):
            with open(self.foursquare_cache, 'rb') as handle:
                # print(f"Loading foursquare data from disk")
                self.foursquare_dict = pickle.load(handle)
        else:
            print(f"No cache found, creating new foursquare dictionary (This may take a while)...")
            self.foursquare_dict = {}

        for index, row in data.iterrows():
            row_key = self.__create_row_key(row)
            if row_key not in self.foursquare_dict:
                if debug_mode:
                    print(f"running {row['Location']} through foursquare.")
                # get GPS location of row
                location = location_tool.lookup_location(row)

                if location:
                    data_foursquare = self.__query_location(location,
                                                            self.__clean_decor_title(row["Location"]),
                                                            debug_mode)
                else:
                    data_foursquare = None

                self.foursquare_dict[row_key] = data_foursquare
            else:
                # it exists, load from cache
                data_foursquare = self.foursquare_dict[row_key]

            if data_foursquare:
                # print(f"found foursquare match for {row_key}")
                data.loc[index, "Foursquare Data"] = json.dumps(data_foursquare)
            else:
                # print(f"NO MATCH found foursquare match for {row_key}")
                data.loc[index, "Foursquare Data"] = None

        with open(self.foursquare_cache, 'wb') as handle:
            pickle.dump(self.foursquare_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

        return data

    @RateLimiter(max_calls=10, period=1)
    def __query(self, latitude, longitude, radius):
        # hacky rate limiter
        limit = 50

        url = f"https://api.foursquare.com/v3/places/search?ll={latitude},{longitude}" \
              f"&radius={radius}" \
              f"&limit={limit}"
        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.api_key}"
        }
        response = requests.request("GET", url, headers=headers).json()
        if "results" in response:
            return response["results"]
        return None

    @RateLimiter(max_calls=10, period=1)
    def __query_location(self, location_osm, location_name, debug_mode=False):
        # convert gps location to a gps bounding box
        min_lat, min_long, max_lat, max_long = self.__location_to_bounding_box(location_osm)
        limit = 25

        # https://developer.foursquare.com/reference/place-search
        url = f"https://api.foursquare.com/v3/places/search?query={urllib.parse.quote(location_name)}" \
              f"&ne={max_lat}%2C{max_long}" \
              f"&sw={min_lat}%2C{min_long}" \
              f"&limit={limit}"

        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.api_key}"
        }
        response = requests.request("GET", url, headers=headers).json()
        if debug_mode:
            print(f"{response}")
        if "results" in response:
            for result in response["results"]:
                if "name" in result:
                    if location_name in result["name"]:
                        return result
        return None

    def __location_to_bounding_box(self, location):
        # print(location.raw)
        min_lat = location.raw["boundingbox"][0]
        max_lat = location.raw["boundingbox"][1]
        min_long = location.raw["boundingbox"][2]
        max_long = location.raw["boundingbox"][3]

        # box = left,bottom,right,top
        # bbox = min Longitude , min Latitude , max Longitude , max Latitude
        # print(f"Output: {min_long},{min_lat},{max_long},{max_lat}")
        return min_lat, min_long, max_lat, max_long

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