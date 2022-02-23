from OSMPythonTools.overpass import overpassQueryBuilder, Overpass
from geopy import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import os.path
import pickle


class LocationTool:
    def __init__(self, email):
        self.email = email
        self.gps_cache = 'caches/gps_cache.pickle'
        self.location_dict = {}

    def make_location_dict(self, df):
        # Initialize Singletons
        locator = Nominatim(user_agent=self.email)
        geocode = RateLimiter(locator, min_delay_seconds=1.5)
        # initialize a dict to cache gps coords for locations
        if os.path.exists(self.gps_cache):
            with open(self.gps_cache, 'rb') as handle:
                # print(f"Loading gps from disk")
                self.location_dict = pickle.load(handle)
        else:
            print(f"No cache found, creating new location dictionary (This may take a while)...")
            self.location_dict = {}
        for index, row in df.iterrows():
            # get GPS location of row
            self.location_dict = self.generate_location_data(row, self.location_dict, locator)
        # save the gps data to disk
        with open(self.gps_cache, 'wb') as handle:
            pickle.dump(self.location_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def generate_location_data(self, row, location_dict, locator):
        city_key = self.create_suburb_state_country_string(row)
        if city_key not in location_dict:
            # print(f"not found: {city_key}")

            # if the gps location does not exist, use geocoding to query. Note that this
            # rate limited and slow, so you only want to query this if totally necessary
            location = locator.geocode(city_key)

            # add the new entry to the location dict
            location_dict[city_key] = location
        else:
            # print(f"found: {city_key}")
            pass
            # if the gps location has already been searched, use the cached version
            # location = location_dict[city_key]

        return location_dict

    def lookup_location(self, row):
        city_key = self.create_suburb_state_country_string(row)
        if city_key in self.location_dict:
            # print(f"found: {city_key}")
            # if the gps location has already been searched, use the cached version
            return self.location_dict[city_key]
        else:
            # print(f"not found: {city_key}")
            return None

    def create_suburb_state_country_string(self, row):
        country = row["Country"]
        state = row["State"]
        suburb = row["Suburb"]
        return f"{suburb}, {state}, {country}"


