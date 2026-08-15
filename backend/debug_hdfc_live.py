"""
Run this after uploading the HDFC PDF to see exactly what text pdfplumber extracts.
Usage: python3 debug_hdfc_live.py <path-to-hdfc.pdf> [password]
"""
import sys, re, io
import pdfplumber

pdf_path = sys.argv[1] if len(sys.argv) > 1 else None
password = sys.argv[2] if len(sys.argv) > 2 else None

if not pdf_path:
    # Try to find the largest PDF in uploads (likely the HDFC one)
    import glob, os
    pdfs = sorted(glob.glob('uploads/*.pdf'), key=os.path.getsize, reverse=True)
    if not pdfs:
        print("No PDFs found in uploads/")
        sys.exit(1)
    pdf_path = pdfs[0]
    print(f"Using: {pdf_path}\n")

try:
    kwargs = {"password": password} if password else {}
    with pdfplumber.open(pdf_path, **kwargs) as pdf:
        print(f"Pages: {len(pdf.pages)}")
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            print(f"\n{'='*60}")
            print(f"PAGE {i} (first 80 chars of each line):")
            print(f"{'='*60}")
            for line in text.splitlines():
                print(f"  [{repr(line[:80])}]")
            
            tables = page.extract_tables()
            if tables:
                print(f"\n  --- {len(tables)} TABLE(S) FOUND ---")
                for j, t in enumerate(tables):
                    print(f"  Table {j} ({len(t)} rows):")
                    for row in t[:5]:
                        print("   ", [str(c)[:30].replace('\n','|') if c else '' for c in row])
except Exception as e:
    print(f"Error: {e}")
    if "password" in str(e).lower():
        print("PDF is password-protected. Run: python3 debug_hdfc_live.py <path> <password>")
