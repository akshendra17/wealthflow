"""
Run this right after uploading the HDFC PDF to capture the backend log output.
It reads the uvicorn process stdout by piping to a file.
"""
import subprocess, json, sys, time

# Get the uvicorn PID
result = subprocess.run(
    ["pgrep", "-f", "uvicorn app.main:app"],
    capture_output=True, text=True
)
pid = result.stdout.strip()
print(f"Uvicorn PID: {pid}")
print("\nWaiting for you to upload the HDFC PDF in the browser...")
print("(watching /proc isn't available on macOS - check the terminal running uvicorn directly)\n")
print("INSTEAD: Look at the uvicorn terminal window. You should see lines like:")
print('  hdfc_pdf_raw_text_preview  lines=[...]')
print("\nIf you don't see that, the HDFC parser isn't being hit at all.")
