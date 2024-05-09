import os
import streamlit as st
import requests
import textract
import PyPDF2
from io import BytesIO

def extract_text_from_file(file_content, file_name):
    text = ""
    if file_name.endswith('.docx'):
        try:
            text = textract.process(BytesIO(file_content)).decode("utf-8")
        except Exception as e:
            st.error(f"Error extracting text from {file_name}: {e}")
    elif file_name.endswith('.pdf'):
        try:
            reader = PyPDF2.PdfFileReader(BytesIO(file_content))
            for page in range(reader.getNumPages()):
                text += reader.getPage(page).extractText()
        except Exception as e:
            st.error(f"Error extracting text from {file_name}: {e}")
    return text

def evaluate_resume(resume_text):
    required_skills = {
        "Core Java": False,
        "Java 8": False,
        "Spring": False,
        "Spring Boot": False,
        "Spring Data": False,
        "JPA": False
    }
    
    optional_skills = {
        "JMS Kafka": False,
        "JWT": False,
        "JWE Encryption": False
    }
    
    for skill in required_skills:
        if skill in resume_text:
            required_skills[skill] = True
            
    for skill in optional_skills:
        if skill in resume_text:
            optional_skills[skill] = True
    
    required_match_percentage = sum(required_skills.values()) / len(required_skills) * 100
    optional_match_percentage = sum(optional_skills.values()) / len(optional_skills) * 100
    
    return required_skills, optional_skills, required_match_percentage, optional_match_percentage

st.title('Resume Analysis')

# Input field for GitHub repository URL
github_url = st.text_input("Enter GitHub repository URL:")

if st.button("Analyze Resumes"):
    if github_url:
        try:
            response = requests.get(f"{github_url}/contents/")
            if response.status_code == 200:
                files = response.json()
                for file in files:
                    file_name = file['name']
                    file_content = requests.get(file['download_url']).content
                    resume_text = extract_text_from_file(file_content, file_name)
                    required_skills, optional_skills, required_match_percentage, optional_match_percentage = evaluate_resume(resume_text)

                    st.subheader(f"Results for resume: {file_name}")

                    st.subheader("Required skills:")
                    for skill, present in required_skills.items():
                        st.write(f"{skill} : {'Yes' if present else 'No'}")

                    st.subheader("Optional Skills:")
                    for skill, present in optional_skills.items():
                        st.write(f"{skill} : {'Yes' if present else 'No'}")

                    st.write("Match % for Required skills:", required_match_percentage)
                    st.write("Match % for Optional Skills:", optional_match_percentage)
                    st.write("-" * 50)
            else:
                st.warning("Failed to fetch files from GitHub repository. Please check the URL.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a GitHub repository URL")
