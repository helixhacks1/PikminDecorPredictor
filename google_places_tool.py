import requests
import urllib.parse
import json
import os.path
import pickle
from decor_to_tag_mapping import google_places_decors_to_tags
from prediction import Prediction
from dataset import Dataset
from ratelimiter import RateLimiter

class GooglePlacesTool:
    def __init__(self, api_key):
        self.api_key = api_key
        self.google_places_cache = 'caches/google_places_cache.pickle'
        self.google_places_dict = {}

    def predict(self, longitude, latitude, radius, seedling_date, burger_shop_start_date, debug_mode=False):
        result = self.__query(longitude=longitude, latitude=latitude, radius=radius)
        ret_dict = {}
        if debug_mode:
            print(f"DEBUG: {result}")

        for element in result:
            # print(f"running on element {element['name']}")
            decors = self.__predict(element, seedling_date, burger_shop_start_date)
            if len(decors) > 0:
                ret_dict[element["name"]] = [x.get_decor() for x in decors]
        return ret_dict

    def predict_row(self, yelp_data, seedling_date, burger_shop_start_date):
        return self.__predict(yelp_data, seedling_date, burger_shop_start_date)

    def __predict(self, google_places_data, seedling_date, burger_shop_start_date):
        decors = []
        if "types" in google_places_data:
            tags = google_places_data["types"]
            for decor_type, tag_list in google_places_decors_to_tags.items():
                result = self.__any_in(tag_list, tags)
                if result is not None:
                    decors.append(Prediction(decor_type, Dataset.google_places, result))
        return decors

    def __any_in(self, list_1, list_2):
        for element in list_1:
            if element in list_2:
                return element
        return None

    def fill_in_data(self, data, location_tool, debug_mode=False):
        # initialize a dict to cache gps coords for locations
        if os.path.exists(self.google_places_cache):
            with open(self.google_places_cache, 'rb') as handle:
                # print(f"Loading google_places data from disk")
                self.google_places_dict = pickle.load(handle)
        else:
            print(f"No cache found, creating new google_places dictionary (This may take a while)...")
            self.google_places_dict = {}

        for index, row in data.iterrows():
            row_key = self.__create_row_key(row)
            if row_key not in self.google_places_dict:
                # get GPS location of row
                location = location_tool.lookup_location(row)

                if location:
                    if debug_mode:
                        print(f"running {row['Location']} through google places.")

                    data_google_places = self.__query_location(location,
                                                               self.__clean_decor_title(row["Location"]))
                else:
                    data_google_places = None

                if debug_mode and data_google_places is not None:
                    print(data_google_places)

                self.google_places_dict[row_key] = data_google_places
            else:
                # it exists, load from cache
                data_google_places = self.google_places_dict[row_key]

            if data_google_places:
                # print(f"found google_places match for {row_key}")
                data.loc[index, "Google Places Data"] = json.dumps(data_google_places)
            else:
                # print(f"NO MATCH found google_places match for {row_key}")
                data.loc[index, "Google Places Data"] = None

        with open(self.google_places_cache, 'wb') as handle:
            pickle.dump(self.google_places_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

        return data

    @RateLimiter(max_calls=10, period=1)
    def __query(self, latitude, longitude, radius):
        url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?" \
              f"location={latitude}%2C{longitude}" \
              f"&radius={radius}" \
              f"&fields=name%2Crating%2Ctypes%2Cgeometry" \
              f"&key={self.api_key}"
        payload = {}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=payload).json()
        if "results" in response:
            return response["results"]
        return None

    @RateLimiter(max_calls=10, period=1)
    def __query_location(self, location_osm, location_name):
        # converting into a bounding box:
        # https://developers.google.com/maps/documentation/places/web-service/search-find-place
        # convert gps location to a gps bounding box
        rectangle_str = self.__create_rect_string(location_osm)

        url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={urllib.parse.quote(location_name)}" \
              f"&inputtype=textquery" \
              f"&locationbias={rectangle_str}" \
              f"&fields=name%2Crating%2Ctypes%2Cgeometry" \
              f"&key={self.api_key}"
        payload = {}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=payload).json()

        if "candidates" in response:
            for result in response["candidates"]:
                if "name" in result:
                    if location_name in result["name"]:
                        return result
        return None

    def __create_rect_string(self, location):
        west = location.raw["boundingbox"][0]
        east = location.raw["boundingbox"][1]
        south = location.raw["boundingbox"][2]
        north = location.raw["boundingbox"][3]
        # in format of rectangle: south, west | north, east
        return urllib.parse.quote(f"rectangle:{south},{west}|{north},{east}")

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