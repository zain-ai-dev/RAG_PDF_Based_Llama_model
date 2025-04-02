# PDF RAG API with Llama 3

[![GitHub stars](https://img.shields.io/github/stars/zain-ai-dev/RAG_PDF_Based_Llama_model?style=social)](https://github.com/zain-ai-dev/RAG_PDF_Based_Llama_model/stargazers)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A high-performance FastAPI application for document intelligence using Llama 3 through Groq's inference API.

![RAG Workflow](https://miro.medium.com/v2/resize:fit:1400/1*5ZLci3SuR0zM_QlZOADv8Q.png)

## ✨ Key Features

- **Multi-format Processing**  
  📄 Handles both text-based and scanned PDFs with OCR fallback
- **Blazing Fast Retrieval**  
  ⚡ FAISS vector store with HuggingFace embeddings
- **Production-Ready API**  
  🚀 Fully async FastAPI endpoints with background processing
- **Real-Time Monitoring**  
  📈 Status tracking for all processed documents

## 🛠️ Installation Guide

### Prerequisites
- Python 3.9+
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [Poppler](https://poppler.freedesktop.org/)
- Groq API key ([Get yours here](https://console.groq.com/))

### Quick Start
```bash
# Clone with your preferred protocol
git clone https://github.com/zain-ai-dev/RAG_PDF_Based_Llama_model.git
cd RAG_PDF_Based_Llama_model

# Setup environment (Linux/macOS)
python -m venv venv
source venv/bin/activate

# Windows users
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Add your GROQ_API_KEY

🏗 Project Architecture
Copy
RAG_PDF_Based_Llama_model/
├── backend/
│   ├── app/
│   │   ├── core/       # App configuration
│   │   ├── models/     # Pydantic schemas
│   │   ├── services/   # Document processing
│   │   ├── static/     # Vector store storage
│   │   ├── utils/      # Helper functions
│   │   ├── main.py     # FastAPI application
│   │   └── routes.py   # API endpoints
├── tests/              # Test cases
└── requirements.txt    # Python dependencies
📡 API Reference
Endpoints
Endpoint	Method	Description	Example
/api/upload/	POST	Process PDF files	See example
/api/query/	POST	Query documents	See example
/api/status/{file_id}	GET	Check processing status	GET /api/status/abc123
Usage Examples
Uploading Documents

bash
Copy
curl -X POST "http://localhost:8000/api/upload/" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@document.pdf"
Querying Documents

bash
Copy
curl -X POST "http://localhost:8000/api/query/" \
  -H "Content-Type: application/json" \
  -d '{"query":"Explain the main concepts"}'
🌟 Advanced Features
Automatic OCR Fallback - Seamlessly handles scanned documents

Background Processing - Non-blocking file ingestion

Vector Store Management - Automatic merging of document embeddings

🤝 Contributing
We welcome contributions! Please follow these steps:

Fork the repository

Create a feature branch (git checkout -b feature/AmazingFeature)

Commit your changes (git commit -m 'Add some AmazingFeature')

Push to the branch (git push origin feature/AmazingFeature)

Open a Pull Request

📜 License
Distributed under the MIT License. See LICENSE for more information.

📬 Contact
Zain AI Dev - @zain-ai-dev
Project Link: https://github.com/zain-ai-dev/RAG_PDF_Based_Llama_model