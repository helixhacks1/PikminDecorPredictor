import pandas as pd
import os
import requests
from datetime import datetime
from sklearn.metrics import classification_report, confusion_matrix
from decor_type import DecorType
from pathlib import Path

class DataTool:

    def load_csv(self, input_file):
        df = pd.read_csv(input_file)
        df["OSM Data"] = None
        df["Foursquare Data"] = None
        df["Google Places Data"] = None
        df["Yelp Data"] = None
        return df

    def generate_directories(self):
        Path("./caches").mkdir(parents=True, exist_ok=True)
        Path("./output").mkdir(parents=True, exist_ok=True)

    def invalidate_caches(self):
        dir = "./caches"
        for f in os.listdir(dir):
            os.remove(os.path.join(dir, f))

    def prepare_dataset_for_predictions(self, df):
        df = df.drop_duplicates(subset=["Location", "Decor", "Country", "State", "Suburb"])
        drop_count = 0
        for index, row in df.iterrows():
            # drop cases where theres no OSM data
            if (row["OSM Data"] is None) \
                    and (row["Foursquare Data"] is None) \
                    and (row["Yelp Data"] is None) \
                    and (row["Google Places Data"] is None):
                # print(f"DROPPING THIS {location}")
                df = df.drop(index)
                drop_count += 1
            elif row["Location"] == row["Suburb"]:
                # print(f"Dropping due to matched location and suburb {location}")
                df = df.drop(index)
                drop_count += 1
        df = self.filter_by_ground_truth(df, [DecorType.forest, DecorType.park, DecorType.waterside])
        print(f"Total number of samples: {len(df.index)}, total number dropped: {drop_count}")
        decors = df['Decor'].copy()
        df = df.drop(columns=['Decor'])
        return decors, df


    def pull_latest_data(self):
        response = requests.get(
            'https://docs.google.com/spreadsheet/ccc?key=1gCrsXoeZ97eGwm9g4_yuB7RXChnKfLqYh1hUJ54Cnjs&output=csv')
        if response.status_code != 200:
            raise Exception(f"Response from google docs failed")
        # saves the raw output to a temp file
        with open('output/latest_output_raw.csv', 'w') as f:
            f.write(str(response.content, 'utf-8'))
        # load the file as input
        with open("output/latest_output_raw.csv", "r") as f:
            lines = f.readlines()
            lines = lines[2:]
            lines[0] = "JUNK_1,Decor,Country,State,Suburb,Location,Date,JUNK_2,JUNK_3,JUNK_4\n"

            output_reformatted = 'output/latest_output_reformatted.csv'
            with open(output_reformatted, 'w') as f_2:
                for item in lines:
                    f_2.write("%s" % item)

            df = pd.read_csv(output_reformatted)
            # map all cafes to one convention
            df.loc[df.Decor == "Café", "Decor"] = "Cafe"

            del df["JUNK_1"]
            del df["JUNK_2"]
            del df["JUNK_3"]
            del df["JUNK_4"]
            df["OSM Data"] = None
            df["Foursquare Data"] = None
            df["Google Places Data"] = None
            df["Yelp Data"] = None
            df.to_csv(f"datasets/dataset_{datetime.now().strftime('%b_%d_%Y')}.csv")
            return df
        return None

    def filter_by_ground_truth(self, data, tags):
        for index, row in data.iterrows():
            for tag in tags:
                if row["Decor"] == tag:
                    data = data.drop(index)
        return data

    def output_to_file(self, df, output_file):
        # save data frame to disk
        df.to_csv(output_file, index=False)

    def analyze_data(self, df, predictions, decors_ground_truth):
        osm_count = 0
        osm_only_count = 0

        foursquare_count = 0
        foursquare_only_count = 0

        google_places_count = 0
        google_places_only_count = 0

        yelp_count = 0
        yelp_only_count = 0
        print("--------------------------------")
        for index, row in df.iterrows():
            if row["OSM Data"]:
                osm_count = osm_count + 1
            if row["OSM Data"] and not row["Foursquare Data"] \
                    and not row["Google Places Data"] and not row["Yelp Data"]:
                osm_only_count = osm_only_count + 1

            if row["Foursquare Data"]:
                foursquare_count = foursquare_count + 1
            if not row["OSM Data"] and row["Foursquare Data"] \
                    and not row["Google Places Data"] and not row["Yelp Data"]:
                foursquare_only_count = foursquare_only_count + 1

            if row["Google Places Data"]:
                google_places_count = google_places_count + 1
            if not row["OSM Data"] and not row["Foursquare Data"] \
                    and row["Google Places Data"] and not row["Yelp Data"]:
                #print(f"{row['Location']} is {decors_ground_truth[index]} for {row['Google Places Data']}")
                google_places_only_count = google_places_only_count + 1

            if row["Yelp Data"]:
                yelp_count = yelp_count + 1
            if not row["OSM Data"] and not row["Foursquare Data"] \
                    and not row["Google Places Data"] and row["Yelp Data"]:
                yelp_only_count = yelp_only_count + 1

            total_count = df.shape[0]
        print(f"Total Samples:{df.shape[0]} "
              f"\nFoursquare Samples: {foursquare_count} ({round(foursquare_count / total_count * 100.0)}%) "
              f"\nGoogle Places Samples: {google_places_count} ({round(google_places_count / total_count * 100.0)}%) "
              f"\nOSM Samples: {osm_count} ({round(osm_count / total_count * 100.0)}%)"
              f"\nYelp Samples: {yelp_count} ({round(yelp_count / total_count * 100.0)}%)"
              f"\n"
              f"\nUnique Foursquare Count: {foursquare_only_count}"
              f"\nUnique Google Places Count: {google_places_only_count}"
              f"\nUnique OSM Count: {osm_only_count}"
              f"\nUnique Yelp Count: {yelp_only_count}")

        # compare the prediction vector and the ground truth, score each class and
        # then print a final score for all labels combined.
        print(confusion_matrix(decors_ground_truth, predictions))
        print(classification_report(decors_ground_truth, predictions))
