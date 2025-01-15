import streamlit as st
import openai
import os
from PyPDF2 import PdfReader
from docx import Document
import pandas as pd

# Set OpenAI API key
try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("API Key for OpenAI is missing. Please configure it in the secrets.")

# Function to load training data from training.txt
def load_training_data(file_path):
    training_data = {}
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                if line.startswith("HỎI:"):
                    question = line.replace("HỎI:", "").strip()
                elif line.startswith("ĐÁP:"):
                    answer = line.replace("ĐÁP:", "").strip()
                    training_data[question] = answer
    else:
        st.warning(f"Training file '{file_path}' not found.")
    return training_data

# Function to process PDF files
def process_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        text = "".join([page.extract_text() for page in reader.pages])
        return text
    except Exception as e:
        st.error(f"Error processing PDF: {e}")
        return ""

# Function to process Word files
def process_word(file_path):
    try:
        doc = Document(file_path)
        text = "".join([p.text for p in doc.paragraphs])
        return text
    except Exception as e:
        st.error(f"Error processing Word file: {e}")
        return ""

# Function to process Excel files
def process_excel(file_path):
    try:
        df = pd.ExcelFile(file_path)
        summary = {}
        for sheet in df.sheet_names:
            data = pd.read_excel(df, sheet_name=sheet)
            summary[sheet] = data.head().to_dict()
        return summary
    except Exception as e:
        st.error(f"Error processing Excel file: {e}")
        return {}

# Streamlit app
st.title("AI Chatbot with File and Link Processing")

# Add logo and introduction
logo_path = "logo.png"  # Path to the logo file
if os.path.exists(logo_path):
    st.image(logo_path, width=150)
st.markdown("""
# Welcome to the AI Chatbot
This chatbot is designed to:
- Respond to questions based on training data.
- Process and extract content from PDF, Word, and Excel files.
- Integrate seamlessly with external links and resources.
""")

# Load training data
training_file = "training.txt"
training_data = load_training_data(training_file)

# User input and submission
user_input = st.text_input("Ask me a question:", key="user_input")
if st.button("Submit") or user_input:
    if user_input:
        try:
            if user_input in training_data:
                response = training_data[user_input]
            else:
                completion = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": user_input}
                    ]
                )
                response = completion["choices"][0]["message"]["content"]
        except Exception as e:
            response = f"Error calling OpenAI API: {e}"

        # Display the response
        st.text_area("Response:", value=response, height=150)

# File upload and processing
uploaded_file = st.file_uploader("Upload a file (PDF, Word, Excel):", type=["pdf", "docx", "xlsx"])
if uploaded_file:
    file_type = uploaded_file.name.split(".")[-1].lower()
    try:
        if file_type == "pdf":
            file_content = process_pdf(uploaded_file)
        elif file_type == "docx":
            file_content = process_word(uploaded_file)
        elif file_type == "xlsx":
            file_content = process_excel(uploaded_file)
            file_content = "\n".join([f"Sheet: {sheet}, Data: {data}" for sheet, data in file_content.items()])
        st.text_area("File Content:", value=file_content, height=300)
    except Exception as e:
        st.error(f"Error processing file: {e}")
