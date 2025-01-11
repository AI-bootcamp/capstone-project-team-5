import streamlit as st
import pdfplumber
import requests

def process_cv_from_pdf(file_path):
    try:
        with pdfplumber.open(file_path) as pdf:
            text = ''
            for page in pdf.pages:
                text += page.extract_text() + '\n'
        return text.strip()
    except Exception as e:
        st.error(f"Error reading PDF file: {e}")
        return None

def extract_basic_info_from_cv(cv_text):
    API_URL = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer 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",
        "Content-Type": "application/json"
    }
    prompt = (
        f"Here is a CV extracted from a PDF file. Please extract the key information: "
        f"name, phone number, and email. If any information is missing, set its value to 'null'.\n\n"
        f"CV Content:\n\n{cv_text}"
    )
    payload = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 200,
        "temperature": 0.2,
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return f"API Error: {response.status_code}, {response.text}"

st.title("PDF CV Information Extractor")
st.write("Upload a PDF CV file to extract key information (Name, Phone, Email).")

uploaded_file = st.file_uploader("Upload your CV (PDF format)", type="pdf")

if uploaded_file is not None:
    cv_text = process_cv_from_pdf(uploaded_file)
    if cv_text:
        extracted_info = extract_basic_info_from_cv(cv_text)
        st.write("Extracted Information:")
        try:
            lines = extracted_info.splitlines()
            name = ""
            phone = ""
            email = ""

            for line in lines:
                if "Name:" in line:
                    name = line.split("Name:")[1].strip()
                elif "Phone:" in line:
                    phone = line.split("Phone:")[1].strip()
                elif "Email:" in line:
                    email = line.split("Email:")[1].strip()

            name = st.text_input("Name:", value=name)
            phone = st.text_input("Phone:", value=phone)
            email = st.text_input("Email:", value=email)

            if st.button("Save Changes"):
                st.success("Information Saved:")
                st.write(f"Name: {name}")
                st.write(f"Phone: {phone}")
                st.write(f"Email: {email}")
        except Exception as e:
            st.error(f"Error in processing the extracted information: {e}")
