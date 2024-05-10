import os
from glob import glob
import PyPDF2
from PyPDF2 import PdfReader
from tqdm import tqdm
import docx
import subprocess


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
    input_dir = os.path.abspath('ug_documents')
    output_dir = os.path.abspath('ug_texts')
    all_wildcard = os.path.join(input_dir, "**/*")
    all_files = glob(all_wildcard, recursive=True)
    all_ext = list(set([os.path.splitext(file)[1] for file in all_files]))
    print("All found extensions:", all_ext)
    pdf_wildcard = os.path.join(input_dir, '**/*.Pdf')
    pdf_files = glob(pdf_wildcard, recursive=True)
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

    docx_wildcard = os.path.join(input_dir, '**/*.Docx')
    docx_files = glob(docx_wildcard, recursive=True)
    for docx_file in tqdm(docx_files):
        file_basename = os.path.basename(docx_file)
        file_name, _ = os.path.splitext(file_basename)
        destination_basename = '{}.txt'.format(file_name)
        destination_file_path = os.path.join(output_dir, destination_basename)
        try:
            full_text = docx_full_text(docx_file)
        except:
            print("Corrupted docx: {}".format(file_basename))
        if not os.path.exists(destination_file_path):
            with open(destination_file_path, 'w') as destination_file:
                destination_file.write(full_text)

    doc_wildcard = os.path.join(input_dir, '**/*.Doc')
    doc_files = glob(doc_wildcard, recursive=True)
    for doc_file in tqdm(doc_files):
        doc_full_text_extract(doc_file, output_dir)

    docm_wildcard = os.path.join(input_dir, '**/*.Docm')
    docm_files = glob(docm_wildcard, recursive=True)
    for docm_file in tqdm(docm_files):
        doc_full_text_extract(docm_file, output_dir)


if __name__ == '__main__':
    main()