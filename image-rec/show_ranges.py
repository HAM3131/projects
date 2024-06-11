import sys
import os
import numpy as np
import cv2
import pdfplumber
from PIL import Image, ImageDraw
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QPushButton, QWidget, QScrollArea
from PyQt5.QtGui import QImage, QPainter, QPen, QPixmap
from PyQt5.QtCore import Qt, QPoint

# Set the environment variable for Qt platform
os.environ['QT_QPA_PLATFORM'] = 'xcb'

class ImageLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.drawing = False
        self.line_drawn = False
        self.setScaledContents(True)  # Allow scaling of the image

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_point = event.pos()
            self.end_point = event.pos()
            self.drawing = True
            self.line_drawn = False

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self.drawing:
            self.end_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.end_point = event.pos()
            self.drawing = False
            self.line_drawn = True
            self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.drawing or self.line_drawn:
            painter = QPainter(self)
            painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
            painter.drawLine(self.start_point, self.end_point)

    def get_line(self):
        if self.line_drawn:
            return self.start_point, self.end_point
        else:
            return None, None

class MainWindow(QMainWindow):
    def __init__(self, pdf_path, page_number, rois, dpi, output_path):
        super().__init__()

        self.pdf_path = pdf_path
        self.page_number = page_number
        self.rois = rois
        self.dpi = dpi
        self.output_path = output_path

        self.setWindowTitle("Skew Correction Tool")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        self.image_label = ImageLabel()
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.image_label)
        layout.addWidget(self.scroll_area)

        self.correct_button = QPushButton("Correct Skew and Save")
        self.correct_button.clicked.connect(self.correct_skew_and_save)
        layout.addWidget(self.correct_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.load_image()

    def load_image(self):
        with pdfplumber.open(self.pdf_path) as pdf:
            page = pdf.pages[self.page_number]
            im = page.to_image(resolution=self.dpi).original

        self.image = im.convert("RGB")
        self.cv_image = np.array(self.image)
        self.cv_image = cv2.cvtColor(self.cv_image, cv2.COLOR_RGB2BGR)

        height, width, channel = self.cv_image.shape
        bytes_per_line = 3 * width
        q_image = QImage(self.cv_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        q_pixmap = QPixmap.fromImage(q_image)  # Convert QImage to QPixmap

        # Scale the pixmap to fit within the window while maintaining aspect ratio
        scaled_pixmap = q_pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(scaled_pixmap)

    def correct_skew_and_save(self):
        start_point, end_point = self.image_label.get_line()
        if start_point and end_point:
            point1 = (start_point.x(), start_point.y())
            point2 = (end_point.x(), end_point.y())

            skew_angle = self.calculate_angle(point1, point2)
            print(f"Detected skew angle: {skew_angle}")

            if skew_angle != 0:
                self.image = self.image.rotate(skew_angle, expand=True, fillcolor='white')

            draw = ImageDraw.Draw(self.image)
            for roi in self.rois.values():
                x0, top, x1, bottom = roi
                draw.rectangle([x0, top, x1, bottom], outline="red", width=5)

            self.image.save(self.output_path)
            print(f"Image with ROIs saved to {self.output_path}")

    def calculate_angle(self, point1, point2):
        delta_y = point2[1] - point1[1]
        delta_x = point2[0] - point1[0]
        angle = np.rad2deg(np.arctan2(delta_y, delta_x))
        return angle

# Define ROIs in pixels (x0, top, x1, bottom)
rois_pixels = {
    "To Whom Paid": (100, 1150, 3000, 1450),
    "Date": (3000, 1100, 4000, 1400),
    "Amount": (4000, 1100, 4900, 1400),
    "Street Address": (100, 1450, 2400, 1750),
    "Purpose": (2400, 1400, 4900, 1700),
    "City": (100, 1700, 2400, 2000),
    "State": (2400, 1700, 2875, 2000),
    "Zip Code": (2875, 1700, 3850, 2000),
    "Check Number": (3850, 1700, 4900, 2000)
}

# Parameters
pdf_path = "./imgs/form.pdf"
page_number = 2  # Third page (adjust as needed)
dpi = 600  # Higher DPI for better resolution
output_path = "./data/page_with_rois.png"

app = QApplication(sys.argv)
window = MainWindow(pdf_path, page_number, rois_pixels, dpi, output_path)
window.show()
sys.exit(app.exec_())
