import pdfplumber
import pandas as pd

# Function to extract text from a specific region
def extract_text_from_region(page, roi):
    text = page.within_bbox(roi).extract_text()
    return text.strip() if text else ""

# Function to extract data from a PDF with a specified page range
def extract_pdf_data(pdf_path, start_page, end_page, rois, dpi=300):
    data = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_number in range(start_page - 1, end_page):
            page = pdf.pages[page_number]
            # Convert pixel values to points (1 inch = 72 points)
            page_data = {field: extract_text_from_region(page, [x * 72 / dpi for x in roi]) for field, roi in rois.items()}
            data.append(page_data)
    return data

# Define ROIs in pixels (x0, top, x1, bottom) based on the gridlines and page inspection
# Adjust these values based on your grid inspection
rois_pixels = {
    "To Whom Paid": (50, 100, 400, 130),
    "Date": (450, 100, 550, 130),
    "Amount": (600, 100, 750, 130),
    "Street Address": (50, 150, 400, 180),
    "Purpose": (450, 150, 750, 180),
    "City": (50, 200, 400, 230),
    "State": (450, 200, 500, 230),
    "Zip Code": (550, 200, 600, 230),
    "Check Number": (650, 200, 750, 230)
}

# Convert pixel ROIs to points (since PDFs are measured in points)
dpi = 600
rois_points = {field: [x * 72 / dpi for x in roi] for field, roi in rois_pixels.items()}

# Define the PDF path and page range
pdf_path = "./imgs/form.pdf"
start_page = 2
end_page = 2

# Extract data from the specified page range
data = extract_pdf_data(pdf_path, start_page, end_page, rois_points, dpi)

# Create a DataFrame and save to CSV
df = pd.DataFrame(data)
csv_path = "./data/output.csv"
df.to_csv(csv_path, index=False)

print("CSV file created:", csv_path)
