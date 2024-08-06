import pytesseract
import pdfplumber
import pandas as pd
from pptx import Presentation
from moviepy.editor import VideoFileClip
import cv2
import numpy as np
from ai71 import AI71

# Configure AI71 API key
AI71_API_KEY = "api71-api-93b91e10-132b-403e-a06c-b9724b62940a"

ai71_client = AI71(AI71_API_KEY)

def summarize_text(text):
    summary = ""
    for chunk in ai71_client.chat.completions.create(
        model="tiiuae/falcon-180b-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Summarize the following text:\n\n{text}"}
        ],
        stream=True,
    ):
        if chunk.choices[0].delta.content:
            summary += chunk.choices[0].delta.content
    return summary.strip()

def extract_entities(text):
    entities = ""
    for chunk in ai71_client.chat.completions.create(
        model="tiiuae/falcon-180b-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Extract entities from the following text:\n\n{text}"}
        ],
        stream=True,
    ):
        if chunk.choices[0].delta.content:
            entities += chunk.choices[0].delta.content
    return entities.strip()

""" def ask_question(context, question):
    answer = ""
    for chunk in ai71_client.chat.completions.create(
        model="tiiuae/falcon-180b-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Answer the following question based on the given context:\n\nContext: {context}\n\nQuestion: {question}"}
        ],
        stream=True,
    ):
        if chunk.choices[0].delta.content:
            answer += chunk.choices[0].delta.content
    return answer.strip() """


def extract_text_from_pdf(pdf_file, page_number=None):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
                text += page.extract_text()
        return text
        if page_number is not None:
            if page_number < len(pdf.pages):
                text = pdf.pages[page_number].extract_text()
        else:
            for page in pdf.pages:
                text += page.extract_text()
    return text


def process_file(file_path, file_type, page_number=None):
    if file_type == 'image':
        # text = extract_text_from_image(file_path)
        print('Found image, doing nothing.')
    elif file_type == 'pdf':
        text = extract_text_from_pdf(file_path, page_number)
    else:
        raise ValueError("Unsupported file type")

    summary = summarize_text(text)
    entities = extract_entities(text)
    return text, summary, entities

# Example usage
file_path = "./uploads/document_06c93e55-bb5c-456b-b3e2-ee07dfa8650c.pdf"
file_type = "pdf"  # Change this based on the file type you are processing
page_number = 0  # For PDF files, set the page number you want to summarize

# text, summary, entities = process_file(file_path, file_type, page_number)
# print("Summary:", summary)
# print("Entities:", entities)

# Extract specific context for question
#topic_no = 236
#topic_context = "the specific text related to topic no 236"  # Extract the specific text here
# Assuming you know the section of the PDF where topic 236 is discussed, replace the above line accordingly
# e.g., topic_context = extract_text_from_pdf(file_path, page_number=236) or similar method

# Asking a question based on the extracted context
#question = f"What is discussed in topic no {236}?"
#answer = ask_question(topic_context, question)
#print("Answer:", answer)