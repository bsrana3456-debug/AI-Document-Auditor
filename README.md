# 🤖 AI-Powered PDF Data Extractor & Auditor

A smart Python-based automation pipeline leveraging **CrewAI multi-agent architecture** and **DeepSeek LLM** to extract, validate, and audit structured financial/document data from unstructured PDF files, exporting clean results directly into CSV format.

## 🚀 Key Features
- **Multi-Agent AI Pipeline**: Utilizes specialized sequential agents (OCR Extractor, Compliance Auditor, and JSON Formatter) to process documents with high accuracy.
- **Smart Data Compliance**: Automatically cleans, normalizes, and validates numerical amounts and document references.
- **Batch Processing**: Automatically scans a dedicated folder (`PDF_Letters`) and processes multiple PDF files in a single run.
- **Enterprise-Friendly Export**: Bypasses heavy data science library dependencies by using native Python libraries to generate clean CSV reports compatible with Microsoft Excel.
- **Secure & Configurable**: Fully privacy-focused with API keys managed via environment variables and robust `.gitignore` rules protecting sensitive logs.

## 🛠️ Tech Stack
- **Python 3.11**
- **CrewAI** (Multi-agent orchestration)
- **DeepSeek API** (via OpenRouter)
- **pdfplumber** (PDF text parsing)
- **Native CSV & OS modules**

## 📂 Project Structure
```text
CrewDemo/
│
├── crew_demo.py          # Main automation script
├── PDF_Letters/          # Input folder for source PDF documents
├── Final_Audit_Report.csv# Generated structured audit output
├── .gitignore            # Excludes virtual environments and raw data
└── README.md             # Project documentation

⚙️ How to Run
Clone the repository:

Bash
git clone [https://github.com/bsrana3456-debug/AI-Data-Auditor.git](https://github.com/bsrana3456-debug/AI-Data-Auditor.git)
Install dependencies:

Bash
pip install crewai pdfplumber
Set your OpenRouter API key in the script:

Python
os.environ["OPENAI_API_KEY"] = "your_api_key_here"
Place your PDF files inside the PDF_Letters folder and run:

Bash
python crew_demo.py

