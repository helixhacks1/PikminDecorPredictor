
from OSMPythonTools.overpass import overpassQueryBuilder, Overpass
from decor_type import DecorType
from decor_to_tag_mapping import osm_decors_to_tags
import math


class OSMTool:
    def __init__(self):
        self.overpass = Overpass()

    def predict_row(self, osm_data, seedling_date, burger_shop_start_date):
        return self.__predict(osm_data, seedling_date, burger_shop_start_date)

    def predict(self, longitude, latitude, radius, seedling_date, burger_shop_start_date, debug_mode=False):
        results = self.__query(longitude, latitude, radius)
        if debug_mode:
            print(f"DEBUG:")
            for element in results:
                print(element.tags())
        ret_dict = {}
        for result in results:
            decors = self.__predict(result, seedling_date, burger_shop_start_date)
            if len(decors) > 0:
                ret_dict[result.tags()["name"]] = decors
        return ret_dict

    def __predict(self, osm_data, seedling_date, burger_shop_start_date):
        decors = []
        for decor_type, tag_list in osm_decors_to_tags.items():
            if decor_type == DecorType.restaurant:
                if osm_data.tag('amenity') == "restaurant" or (
                        seedling_date < burger_shop_start_date and osm_data.tag('amenity') == "fast_food"):
                    # early data shows that fast_food was originally used as restaurant.
                    # Need a bit more data to verify the pattern.
                    decors.append(DecorType.restaurant)
            elif decor_type == DecorType.burger_place:
                if (seedling_date >= burger_shop_start_date and osm_data.tag('amenity') == "fast_food") or osm_data.tag(
                        'cuisine') == 'burger':
                    decors.append(DecorType.burger_place)
            else:
                for tag in tag_list:
                    if osm_data.tag(tag[0]) == tag[1]:
                        decors.append(decor_type)
        return list(set(decors))

    def fill_in_data(self, df, location_tool):
        for index, row in df.iterrows():
            # get GPS location of row
            location = location_tool.lookup_location(row)
            if location:
                data_osm = self.__query_location(location, self.__clean_decor_title(row["Location"]))
            else:
                data_osm = None

            df.loc[index, "OSM Data"] = data_osm
            if data_osm:
                df.loc[index, "OSM Tags"] = str(data_osm.tags())
        return df

    def __query(self, longitude, latitude, radius):
        min_long, min_lat, max_long, max_lat = self.__longitude_latitude_radius_to_bounding_box(longitude,
                                                                                                latitude,
                                                                                                radius)
        # https://wiki.openstreetmap.org/wiki/Overpass_API/Language_Guide
        results = []
        for selector in ["amenity", "shop", "aeroway", "tourism", "cuisine", "leisure", "natural", "railway"]:
            query = overpassQueryBuilder(bbox=[min_lat, min_long, max_lat, max_long],
                                         selector=[f'"{selector}"'],
                                         elementType='node',
                                         out='body')
            result = self.overpass.query(query, timeout=60)
            if result.elements():
                results = list(set(results + result.elements()))
        # https://github.com/mocnik-science/osm-python-tools/issues/39
        return results

    def __query_location(self, location_osm, location_name):
        # convert gps location to a gps bounding box
        min_long, min_lat, max_long, max_lat = self.__location_to_bounding_box(location_osm)

        # NOTE: this is why we aren't passing a completed bounding box object. For some reason,
        # overpassQueryBuilder breaks OSM standard and puts lat before long, reference:
        # https://github.com/mocnik-science/osm-python-tools/issues/14
        # full docs for this function: https://github.com/mocnik-science/osm-python-tools/blob/master/docs/overpass.md
        query = overpassQueryBuilder(bbox=[min_lat, min_long, max_lat, max_long],
                                     elementType='node',
                                     selector=[f'"name"~"{location_name}"'],
                                     out='body')
        result = self.overpass.query(query, timeout=60)
        # print(f"query complete for {location} with elements: {len(result.elements())}")
        for element in result.elements():
            if location_name in element.tag('name'):
                # exact match for substring!
                return element

        if len(result.elements()) > 0:
            print(f"Unmatched tag: {result.elements()[0].tags()}")
        # no match, return None.
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
        return min_long, min_lat, max_long, max_lat

    def __longitude_latitude_radius_to_bounding_box(self, longitude, latitude, radius):

        radius_latitude = abs(radius / 111320) / 2
        radius_longitude = abs(radius / (40075000 * math.cos(latitude) / 360)) / 2
        # print(f"longitude : {radius_longitude} and latitude {radius_latitude}")

        # print(location.raw)
        min_lat = latitude - radius_latitude
        max_lat = latitude + radius_latitude
        min_long = longitude - radius_longitude
        max_long = longitude + radius_longitude

        # box = left,bottom,right,top
        # bbox = min Longitude , min Latitude , max Longitude , max Latitude
        # print(f"Output: {min_long},{min_lat},{max_long},{max_lat}")
        return min_long, min_lat, max_long, max_lat


    def __clean_decor_title(self, title):
        if title.startswith("Near "):
            return title[5:]
        elif title.startswith("near "):
            return title[5:]
        else:
            return title

    def __pretty_print_osm_element(self, element):
        print(f"OSM Name: {element.tag('name')}")
        print("-----------------------------")
        did_print = False
        if element.tag('aeroway'):
            did_print = True
            print(f"aeroway: {element.tag('aeroway')}")
        if element.tag('amenity'):
            did_print = True
            print(f"amenity: {element.tag('amenity')}")
        if element.tag('leisure'):
            did_print = True
            print(f"leisure: {element.tag('park')}")
        if element.tag('natural'):
            did_print = True
            print(f"natural: {element.tag('natural')}")
        if element.tag('railway'):
            did_print = True
            print(f"railway: {element.tag('railway')}")
        if element.tag('shop'):
            did_print = True
            print(f"shop: {element.tag('shop')}")
        if element.tag('tourism'):
            did_print = True
            print(f"tourism: {element.tag('tourism')}")
        if not did_print:
            print(f"ID: {element.id()}")
            print(f"Type: {element.type()}")
        print("----")
        print(f"Tags {element.tags()}")
        print("-----------------------------")
        print("")


