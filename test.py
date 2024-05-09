import os
import streamlit as st
import textract
import PyPDF2
import requests
from io import BytesIO

def extract_text_from_file(file_path):
    text = ""
    if file_path.endswith('.docx') or file_path.endswith('.pdf'):
        try:
            if file_path.endswith('.docx'):
                text = textract.process(file_path).decode("utf-8")
            elif file_path.endswith('.pdf'):
                with open(file_path, "rb") as f:
                    reader = PyPDF2.PdfFileReader(f)
                    for page in range(reader.getNumPages()):
                        text += reader.getPage(page).extractText()
        except Exception as e:
            st.error(f"Error extracting text from {file_path}: {e}")
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
repo_url = st.text_input("Enter GitHub repository URL:")

if st.button("Analyze Resumes"):
    if repo_url:
        # Construct the URL to fetch the files from GitHub
        api_url = f"{repo_url}/contents/"
        response = requests.get(api_url)
        
        if response.status_code == 200:
            for item in response.json():
                if item["type"] == "file":
                    resume_url = item["download_url"]
                    resume_file_name = item["name"]
                    resume_content = requests.get(resume_url).content
                    resume_file = BytesIO(resume_content)
                    if (resume_file_name.endswith('.docx') or resume_file_name.endswith('.pdf')):
                        resume_text = extract_text_from_file(resume_file)
                        required_skills, optional_skills, required_match_percentage, optional_match_percentage = evaluate_resume(resume_text)

                        st.subheader(f"Results for resume: {resume_file_name}")

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
            st.error("Failed to fetch files from GitHub repository. Please check the URL.")
    else:
        st.warning("Please enter the GitHub repository URL")
