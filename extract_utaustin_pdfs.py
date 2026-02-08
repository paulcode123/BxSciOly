import os
import fitz  # PyMuPDF

def extract_pdf_text(pdf_path, output_path):
    """Extract text from a PDF file and save to a text file."""
    try:
        doc = fitz.open(pdf_path)
        text_content = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            text_content.append(text)
        
        doc.close()
        
        # Write all text to output file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(text_content))
        
        print(f"[OK] Extracted text from {os.path.basename(pdf_path)} -> {os.path.basename(output_path)}")
        return True
    except Exception as e:
        print(f"[ERROR] Error processing {os.path.basename(pdf_path)}: {str(e)}")
        return False

def main():
    # Define paths for UTAustin
    pdf_dir = "TestBase/UTAustin/TestsPDF"
    output_dir = "TestBase/UTAustin/TestsTXT"
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all PDF files
    pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
    
    # Filter out Images and Alibis PDFs (optional - comment out if you want all PDFs)
    # pdf_files = [f for f in pdf_files if 'Images' not in f and 'Alibis' not in f]
    
    if not pdf_files:
        print(f"No PDF files found in {pdf_dir}")
        return
    
    print(f"Found {len(pdf_files)} PDF file(s) to process...\n")
    
    # Process each PDF
    success_count = 0
    for pdf_file in sorted(pdf_files):
        pdf_path = os.path.join(pdf_dir, pdf_file)
        # Create output filename by replacing .pdf with .txt
        txt_filename = pdf_file.replace('.pdf', '.txt').replace('.PDF', '.txt')
        output_path = os.path.join(output_dir, txt_filename)
        
        if extract_pdf_text(pdf_path, output_path):
            success_count += 1
    
    print(f"\n[SUCCESS] Successfully extracted text from {success_count}/{len(pdf_files)} PDF file(s)")

if __name__ == "__main__":
    main()

