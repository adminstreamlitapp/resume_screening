import os
import streamlit as st
import requests
import textract
from PyPDF2 import PdfReader

def extract_text_from_file(file_url):
    text = ""
    try:
        response = requests.get(file_url)
        response.raise_for_status()
        content = response.content
        if file_url.endswith('.docx'):
            with open("temp.docx", "wb") as f:
                f.write(content)
            text = textract.process("temp.docx").decode("utf-8")
        elif file_url.endswith('.pdf'):
            with open("temp.pdf", "wb") as f:
                f.write(content)
            reader = PdfReader("temp.pdf")
            for page in reader.pages:
                text += page.extract_text()
    except Exception as e:
        st.error(f"Error extracting text from {file_url}: {e}")
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

st.title('GitHub Resume Analysis')

# Input field for GitHub repository URL
repo_url = st.text_input("Enter GitHub repository URL:")
analyze_resumes = st.button("Analyze Resumes")

if analyze_resumes:
    if not repo_url:
        st.warning("Please enter GitHub repository URL.")
    else:
        try:
            response = requests.get(repo_url)
            response.raise_for_status()
            files = response.json()
            
            # Display file info
            for file_info in files:
                if file_info["name"].endswith(('.docx', '.pdf')):
                    file_url = file_info["download_url"]
                    resume_text = extract_text_from_file(file_url)
                    required_skills, optional_skills, required_match_percentage, optional_match_percentage = evaluate_resume(resume_text)

                    st.subheader(f"Results for resume: {file_info['name']}")
                    st.write("Required skills:")
                    for skill, present in required_skills.items():
                        st.write(f"{skill} : {'Yes' if present else 'No'}")

                    st.write("Optional Skills:")
                    for skill, present in optional_skills.items():
                        st.write(f"{skill} : {'Yes' if present else 'No'}")

                    st.write("Match % for Required skills:", required_match_percentage)
                    st.write("Match % for Optional Skills:", optional_match_percentage)
                    st.write("-" * 50)
        except Exception as e:
            st.error(f"Failed to fetch files from GitHub repository. Please check the URL.")
