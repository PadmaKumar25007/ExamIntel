import pdfplumber
import re
import spacy

nlp = spacy.load("en_core_web_sm")

def clean_text(text):
    text = re.sub(r'\d+', '', text)  # remove numbers
    text = re.sub(r'\W+', ' ', text)  # remove special characters
    return text.lower()

def extract_text_from_pdfs(uploaded_files):
    all_text = {}

    for file in uploaded_files:
        text = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + " "

        cleaned = clean_text(text)
        all_text[file.name] = cleaned

    return all_text