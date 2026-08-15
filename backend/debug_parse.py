import asyncio
from app.core.services.statement_parser import parse_pdf
import os

pdf_path = "/Users/akshendrakumar/Projects/wealthflow/backend/uploads/646b470b-f764-4dd4-a511-a582b8c823d3.pdf"
with open(pdf_path, 'rb') as f:
    try:
        res = parse_pdf(f.read())
        print(f"Parsed {len(res.transactions)} txns")
    except Exception as e:
        import traceback
        traceback.print_exc()
