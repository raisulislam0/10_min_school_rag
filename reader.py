import os
import numpy as np
from pdf2image import convert_from_path
import easyocr

poppler_path = os.path.join(os.getcwd(), 'poppler-24.08.0', 'Library', 'bin')
# --- CONFIG -------------------------------------------------
PDF_PATH = "hsc.pdf"  
OUTPUT_TXT = "bangla_easyocr_output.txt"
POPPLER_PATH = poppler_path  
LANGS = ['bn', 'en']  
DPI = 300
# ------------------------------------------------------------

def extract_text_from_pdf(
    pdf_path: str,
    output_txt: str = OUTPUT_TXT,
    poppler_path: str = POPPLER_PATH,
    langs=None,
    dpi: int = DPI,
):
    if langs is None:
        langs = ['bn']

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    print("📄 Converting PDF to images...")
    images = convert_from_path(pdf_path, dpi=dpi, poppler_path=poppler_path)
    num_pages = len(images)
    print(f"🧾 Total pages: {num_pages}")

    print("⚙️ Loading EasyOCR reader...")
    reader = easyocr.Reader(langs, gpu=True)  # set gpu=True if you have CUDA

    all_text = []

    for idx, image in enumerate(images, start=1):
        if idx < 3 or idx > 19:
            continue
        else:
            print(f"🔍 Processing page {idx}/{num_pages}...")
            np_img = np.array(image)
            page_lines = reader.readtext(np_img, detail=0, paragraph=True)
            page_text = "\n".join(page_lines).strip()
            all_text.append(f"--- Page {idx} ---\n{page_text}")

    final_text = "".join(all_text)

    with open(output_txt, "w", encoding="utf-8") as f:
        f.write(final_text)

    print(f"✅ Extracted text saved to: {output_txt}")

if __name__ == "__main__":
    extract_text_from_pdf(PDF_PATH)
