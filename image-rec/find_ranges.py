import pdfplumber
import matplotlib.pyplot as plt
from PIL import Image

# Function to draw gridlines and labels on the PDF page image
def save_pdf_page_with_gridlines(pdf_path, page_number, dpi, grid_size, output_path):
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_number]
        im = page.to_image(resolution=dpi).original

        # Convert the image to RGB format for matplotlib compatibility
        im_rgb = im.convert("RGB")

        # Get the dimensions of the image
        width, height = im_rgb.size

        # Plot the image using matplotlib
        fig, ax = plt.subplots(figsize=(width / dpi, height / dpi))
        ax.imshow(im_rgb)

        # Draw gridlines and labels
        for x in range(0, width, grid_size):
            ax.axvline(x, color='r', linestyle='--', linewidth=0.5)
            if x % 100 == 0:
                ax.text(x, 0, str(x), color='red', fontsize=8, ha='center', va='top', backgroundcolor='white')
        for y in range(0, height, grid_size):
            ax.axhline(y, color='r', linestyle='--', linewidth=0.5)
            if y % 100 == 0:
                ax.text(0, y, str(y), color='red', fontsize=8, ha='left', va='center', backgroundcolor='white')

        # Save the image with gridlines and labels
        plt.savefig(output_path, bbox_inches='tight')
        plt.close()

# Parameters
pdf_path = "./imgs/form.pdf"
page_number = 2  # First page (adjust as needed)
dpi = 600  # Higher DPI for better resolution
grid_size = 50  # Grid size in pixels
output_path = "./data/page_with_gridlines.png"

# Save the PDF page with gridlines and labels
save_pdf_page_with_gridlines(pdf_path, page_number, dpi, grid_size, output_path)

print(f"Image with gridlines saved to {output_path}")
