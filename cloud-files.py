import os
import streamlit as st
import textract
import PyPDF2
from docx import Document

def extract_text_from_file(file):
    text = ""
    if file.name.endswith('.docx') or file.name.endswith('.pdf'):
        try:
            if file.name.endswith('.docx'):
                doc = Document(file)
                for paragraph in doc.paragraphs:
                    text += paragraph.text
            elif file.name.endswith('.pdf'):
                reader = PyPDF2.PdfFileReader(file)
                for page in range(reader.getNumPages()):
                    text += reader.getPage(page).extractText()
        except Exception as e:
            st.error(f"Error extracting text from {file.name}: {e}")
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

# File uploader for resumes
resume_files = st.file_uploader("Upload your resumes", accept_multiple_files=True, type=['docx', 'pdf'])

if st.button("Analyze Resumes"):
    if resume_files:
        for resume_file in resume_files:
            resume_text = extract_text_from_file(resume_file)
            required_skills, optional_skills, required_match_percentage, optional_match_percentage = evaluate_resume(resume_text)

            st.subheader(f"Results for resume: {resume_file.name}")

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
        st.warning("Please upload resumes to analyze")
