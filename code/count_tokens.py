import sys
import os
import tiktoken
from glob import glob
from tqdm import tqdm


MODEL = "gpt-4o-mini-2024-07-18"


def count_tokens(tokenizer, text):
    return len(tokenizer.encode(text))


def main(txt_files_input_path):
    tokenizer = tiktoken.encoding_for_model(MODEL)
    input_dir = os.path.abspath(txt_files_input_path)
    txt_wildcard = os.path.join(input_dir, '*.txt')
    txt_files = glob(txt_wildcard)

    full_text_list = list()
    for txt_file_path in tqdm(txt_files):
        with open(txt_file_path, 'r') as txt_file:
            full_text_list.append(txt_file.read())

    full_text = "\n".join(full_text_list)
    token_count = count_tokens(tokenizer, full_text)
    token_cost = 0.15
    token_cost_per = 1000000
    print(
        "This will use at least {} tokens and cost at least ${} to run using model {}.".format(
            token_count, round((token_count / token_cost_per) * token_cost, 2), MODEL
        )
    )


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Enter text file input path as first positional argument.")
    else:
        main(sys.argv[1])