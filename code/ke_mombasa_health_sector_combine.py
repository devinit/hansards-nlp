import os
import json
from glob import glob
import pandas as pd


def main():
    data_list = list()
    json_response_files = glob("ke_mombasa_health_json_responses/*.json")
    for json_response_file in json_response_files:
        file_basename, _ = os.path.splitext(os.path.basename(json_response_file))
        with open(json_response_file) as json_file:
            file_json = json.load(json_file)
            file_json["filename"] = file_basename
            data_list.append(file_json)
    df = pd.DataFrame.from_records(data_list)
    df.to_csv('data/ke_mombasa_health_sector.csv', index=False)


if __name__ == '__main__':
    main()