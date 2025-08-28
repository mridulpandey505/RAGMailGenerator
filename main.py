import streamlit as st
from langchain_community.document_loaders import WebBaseLoader

from chains import Chain
from port import ResumePortfolio
from cleaner import clean_text
import tempfile
from dotenv import load_dotenv

load_dotenv()


def create_streamlit_app(chain, port, clean_text):
    st.title("RAG based Mail Generator")
    url_input = st.text_input("Enter a URL:", value="https://jobs.nike.com/job/R-33460")
    resume_inp = st.file_uploader("enter resume as pdf ", type = ['pdf'])
    
    submit_button = st.button("Submit")

    if submit_button :
        try:
            loader = WebBaseLoader([url_input])
            data = clean_text(loader.load().pop().page_content)
            if resume_inp is not None:
    
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(resume_inp.read())
                    temp_path = tmp.name
            port.load_resume(temp_path)   # to vector store
            jobs = chain.extract_jobs(data)
            for job in jobs:
                skills = job.get('skills', [])
                links = port.query_resume(skills)
                email = chain.write_mail(job, links)
                # st.code(email, language='markdown')
                st.text_area(email)
                break
        except Exception as e:
            st.error(f"An Error Occurred: {e}")


if __name__ == "__main__":
    chain = Chain()
    portfolio = ResumePortfolio()
    st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")
    create_streamlit_app(chain, portfolio, clean_text)