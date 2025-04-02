# setup.py in RAG_PDF_Based_Llama_model/
from setuptools import setup, find_packages

setup(
    name="rag_app",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        # List all your dependencies here
        "fastapi",
        "uvicorn",
        # etc.
    ],
)