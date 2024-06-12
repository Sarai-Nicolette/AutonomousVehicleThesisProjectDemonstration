import json
import os
import numpy as np
import pandas as pd


class ImportRotorcraftData:
    def __init__(self, s_fn, d_fn):
        self.specs_filename = s_fn
        self.data_filename = d_fn

    def get_rotorcraft_data(self):
        print("Fetching Rotorcraft Data")
        JSON_FILE_NAME = self.specs_filename
        CSV_FILE_NAME = self.data_filename
        FILE_LOCATION = os.getcwd() + "/variables/"
        print(FILE_LOCATION)
        # Grab json file
        with open(FILE_LOCATION + JSON_FILE_NAME, "r", encoding="utf-8") as rotor_info:
            json_data = json.load(rotor_info)

        # Try to open detailed rotorcraft data
        csv_data = []
        try:
            csv_data = pd.read_csv(FILE_LOCATION + CSV_FILE_NAME, dtype=np.float64)

        except FileNotFoundError:

            pass

        return json_data, csv_data

