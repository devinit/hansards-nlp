import os
from glob import glob
import PyPDF2
from PyPDF2 import PdfReader
import docx
from tqdm import tqdm

def pdf_full_text(pdf_path):
    pdf_reader = PdfReader(pdf_path)
    text_list = list()
    for page in pdf_reader.pages:
        text_list.append(page.extract_text())
    return '\n'.join(text_list).replace('\x00','')


def docx_full_text(docx_path):
    doc = docx.Document(docx_path)
    text_list = list()
    for para in doc.paragraphs:
        text_list.append(para.text)
    return '\n'.join(text_list).replace('\x00','')


def main():
    input_dir = os.path.abspath('ke_documents')
    output_dir = os.path.abspath('ke_texts')
    pdf_wildcard = os.path.join(input_dir, '*.pdf')
    pdf_files = glob(pdf_wildcard)
    for pdf_file in tqdm(pdf_files):
        file_basename = os.path.basename(pdf_file)
        file_name, _ = os.path.splitext(file_basename)
        try:
            full_text = pdf_full_text(pdf_file)
        except PyPDF2.errors.PdfReadError:
            print("Corrupted PDF: {}".format(file_basename))
        destination_basename = '{}.txt'.format(file_name)
        destination_file_path = os.path.join(output_dir, destination_basename)
        with open(destination_file_path, 'w') as destination_file:
            destination_file.write(full_text)

    docx_wildcard = os.path.join(input_dir, '*.docx')
    docx_files = glob(docx_wildcard)
    for docx_file in tqdm(docx_files):
        file_basename = os.path.basename(docx_file)
        file_name, _ = os.path.splitext(file_basename)
        try:
            full_text = docx_full_text(docx_file)
        except:
            print("Corrupted docx: {}".format(file_basename))
        destination_basename = '{}.txt'.format(file_name)
        destination_file_path = os.path.join(output_dir, destination_basename)
        with open(destination_file_path, 'w') as destination_file:
            destination_file.write(full_text)


if __name__ == '__main__':
    main()