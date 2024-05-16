import os
from glob import glob
from tqdm import tqdm
import torch
from sentence_transformers import SentenceTransformer
from nltk.tokenize import sent_tokenize
import numpy as np
import re
from datetime import datetime
import pickle
from datasets import Dataset
from datasets.utils.logging import disable_progress_bar
disable_progress_bar()


global MODEL
global DEVICE
MODEL = SentenceTransformer("Snowflake/snowflake-arctic-embed-s")
DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"
MODEL = MODEL.to(DEVICE)


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


def main(txt_files_input_path, query, threshold=0.6):
    pickle_path = os.path.join("large_data", "{}.pkl".format(txt_files_input_path))
    input_dir = os.path.abspath(txt_files_input_path)
    txt_wildcard = os.path.join(input_dir, '*.txt')
    txt_files = glob(txt_wildcard)

    full_text_list = list()
    for txt_file_path in tqdm(txt_files):
        with open(txt_file_path, 'r') as txt_file:
            full_text_list.append(txt_file.read())

    sentences = list()
    sentence_filenames = list()
    for i, full_text in enumerate(full_text_list):
        filename = os.path.basename(txt_files[i])
        file_sentences = sent_tokenize(full_text)
        sentences += file_sentences
        sentence_filenames += [filename] * len(file_sentences)


    if os.path.exists(pickle_path):
        with open(pickle_path, 'rb') as pickle_file:
            file_embeddings = pickle.load(pickle_file)
    else:
        file_embeddings = list()
        for sentence in tqdm(sentences):
            embedding = MODEL.encode(sentence)
            file_embeddings.append(embedding)
        with open(pickle_path, 'wb') as pickle_file:
            pickle.dump(file_embeddings, pickle_file)

    query_embedding = MODEL.encode(query, prompt_name="query")
    ranks = np.zeros(len(file_embeddings))
    for i, embedding in enumerate(file_embeddings):
        ranks[i] = query_embedding @ embedding.T

    dataset = Dataset.from_dict(
        {
            'text': sentences,
            'filename': sentence_filenames,
            'rank': ranks
        }
    )

    matching_dataset = dataset.filter(lambda example: example['rank'] > threshold)
    unique_matching_files = list(set(matching_dataset['filename']))
    
    if matching_dataset.num_rows == 0:
        print("No matches.")
    else:
        for matching_file in unique_matching_files:
            print("FILE: {}".format(matching_file))
            file_dataset = matching_dataset.filter(lambda example: example['filename'] == matching_file)
            for sentence in file_dataset['text']:
                print(sentence)
            print("\n")


if __name__ == '__main__':
    query = "What are challenges with health service delivery?"
    main("ke_texts", query)