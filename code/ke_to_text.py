import os
from glob import glob
import PyPDF2
from PyPDF2 import PdfReader
from tqdm import tqdm
import re
import subprocess


def remove_control_characters(text):
    # Define a regular expression pattern to match control characters
    pattern = re.compile(r'[\x00-\x1F]')

    # Use sub() function to replace matched control characters with an empty string
    cleaned_text = pattern.sub('', text)
    
    return cleaned_text


def pdf_full_text(pdf_path):
    pdf_reader = PdfReader(pdf_path)
    text_list = list()
    for page in pdf_reader.pages:
        text_list.append(page.extract_text())
    return remove_control_characters('\n'.join(text_list))


def doc_full_text_extract(doc_path, outdir):
    file_basename = os.path.basename(doc_path)
    file_name, _ = os.path.splitext(file_basename)
    destination_basename = '{}.txt'.format(file_name)
    destination_file_path = os.path.join(outdir, destination_basename)
    if not os.path.exists(destination_file_path):
        command_run = subprocess.call(['libreoffice', '--convert-to', 'txt', doc_path, '--outdir', outdir], stdout=subprocess.PIPE)
        if command_run != 0:
            print("Corrupted doc: {}".format(file_basename))


def main():
    input_dir = os.path.abspath('ke_documents')
    output_dir = os.path.abspath('ke_texts')
    pdf_wildcard = os.path.join(input_dir, '*.pdf')
    pdf_files = glob(pdf_wildcard)
    for pdf_file in tqdm(pdf_files):
        file_basename = os.path.basename(pdf_file)
        file_name, _ = os.path.splitext(file_basename)
        destination_basename = '{}.txt'.format(file_name)
        destination_file_path = os.path.join(output_dir, destination_basename)
        if not os.path.exists(destination_file_path):
            try:
                full_text = pdf_full_text(pdf_file)
            except PyPDF2.errors.PdfReadError:
                print("Corrupted PDF: {}".format(file_basename))
            with open(destination_file_path, 'w') as destination_file:
                destination_file.write(full_text)

    docx_wildcard = os.path.join(input_dir, '*.docx')
    docx_files = glob(docx_wildcard)
    for docx_file in tqdm(docx_files):
        doc_full_text_extract(docx_file, output_dir)


if __name__ == '__main__':
    main()