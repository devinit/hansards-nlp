import os
import json
from glob import glob
import pandas as pd
import re
from datetime import datetime


def extract_date_from_filename(filename):
    # Define the pattern to match the date in the filename
    pattern = r'Hansard(?:,)?\s+(\w+\s+\d+,\s+\d{4})'
    
    # Search for the pattern in the filename
    match = re.search(pattern, filename, re.IGNORECASE)
    
    if match:
        # Extract the matched date string
        date_string = match.group(1)
        
        # Parse the date string into a datetime object
        date_format = '%B %d, %Y'  # Format of the date string
        date_object = datetime.strptime(date_string, date_format)
        
        # Return the date in YYYY-MM-DD format
        return date_object.strftime('%Y-%m-%d')
    else:
        return None


def main():
    data_list = list()
    json_response_files = glob("ke_health_json_responses/*.json")
    for json_response_file in json_response_files:
        file_date = extract_date_from_filename(json_response_file)
        file_basename, _ = os.path.splitext(os.path.basename(json_response_file))
        with open(json_response_file) as json_file:
            file_json = json.load(json_file)
            file_json["date"] = file_date
            file_json["filename"] = file_basename
            data_list.append(file_json)
    df = pd.DataFrame.from_records(data_list)
    df.to_csv('data/ke_health_sector.csv', index=False)


if __name__ == '__main__':
    main()