"""
Run this to inspect the HDFC PDF:
  python3 debug_hdfc_password.py <path-to-pdf> <password>
"""
import sys, io, glob, os
import pdfplumber

pdf_path = sys.argv[1] if len(sys.argv) > 1 else None
password = sys.argv[2] if len(sys.argv) > 2 else None

if not pdf_path:
    pdfs = sorted(glob.glob('uploads/*.pdf'), key=os.path.getsize, reverse=True)
    pdf_path = pdfs[-1] if pdfs else None
    print(f"Using: {pdf_path}")

if not pdf_path:
    print("No PDF found")
    sys.exit(1)

try:
    kwargs = {"password": password} if password else {}
    with pdfplumber.open(pdf_path, **kwargs) as pdf:
        print(f"Pages: {len(pdf.pages)}\n")
        for i, page in enumerate(pdf.pages[:2]):
            print(f"{'='*70}")
            print(f"PAGE {i} — RAW LINES:")
            print(f"{'='*70}")
            text = page.extract_text() or ""
            for j, line in enumerate(text.splitlines()):
                print(f"  L{j:03}: {repr(line)}")

            print(f"\nPAGE {i} — TABLES:")
            for j, table in enumerate(page.extract_tables()):
                print(f"  Table {j} ({len(table)} rows):")
                for row in table[:10]:
                    print("    ", [repr(str(c or '')[:40]) for c in row])
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    if "password" in str(e).lower() or "PDFPasswordIncorrect" in type(e).__name__:
        print("\nThis PDF needs a password. Run:")
        print(f"  python3 debug_hdfc_password.py '{pdf_path}' YOUR_PASSWORD")
