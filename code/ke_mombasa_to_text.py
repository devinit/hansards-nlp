import os
from glob import glob
import PyPDF2
from PyPDF2 import PdfReader
from tqdm import tqdm

def pdf_full_text(pdf_path):
    pdf_reader = PdfReader(pdf_path)
    text_list = list()
    for page in pdf_reader.pages:
        text_list.append(page.extract_text())
    return '\n'.join(text_list).replace('\x00','')


def main():
    input_dir = os.path.abspath('mombasa_documents')
    output_dir = os.path.abspath('mombasa_texts')
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    all_wildcard = os.path.join(input_dir, "**/*")
    all_files = glob(all_wildcard, recursive=True)
    all_ext = list(set([os.path.splitext(file)[1] for file in all_files]))
    print("All found extensions:", all_ext)

    pdf_wildcard = os.path.join(input_dir, '*.pdf')
    pdf_files = glob(pdf_wildcard)
    for pdf_file in tqdm(pdf_files):
        file_basename = os.path.basename(pdf_file)
        file_name, _ = os.path.splitext(file_basename)
        destination_basename = '{}.txt'.format(file_name)
        destination_file_path = os.path.join(output_dir, destination_basename)
        try:
            full_text = pdf_full_text(pdf_file)
        except PyPDF2.errors.PdfReadError:
            print("Corrupted PDF: {}".format(file_basename))
        if not os.path.exists(destination_file_path):
            with open(destination_file_path, 'w') as destination_file:
                destination_file.write(full_text)

if __name__ == '__main__':
    main()