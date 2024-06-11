
# GNU LGPL Version 2.1
#
# QrCards.py
# Author: K0tak0tak0
# Email: kotako@kotakostudio.com
# Date: 2024-06-10
#
# This software is distributed under the GNU Lesser General Public License version 2.1.
# For more details, see <https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html>.
#
# Description:
# This script generates membership cards with QR codes using PyQt5 and ReportLab.
# The QR codes are generated based on unique numbers stored in an SQLite database.

import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QDoubleSpinBox, QFileDialog, QFormLayout, QSpinBox
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import qrcode
from PIL import Image
from io import BytesIO
from reportlab.lib.pagesizes import portrait, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
import random
import datetime

######################################################################
##################### Document configuration #########################
######################################################################

ppi = 72 # Points Per Inch

card_width_cm = 9 # Card width in centimeters
card_height_cm = 5 # Card height in centimeters

rows = 8 # Number of rows in the document
cols = 3 # Number of columns in the document

# These two values are set in inches because it's much easier to find paper sizes in imperial. if you want to set them in metric do (〇〇 * 2.54)
page_width = 11 # Page width in INCHES
page_height = 17 # Page height in INCHES

# set the orientation of the PDF pages to portrait or landscape
orientation = portrait

######################################################################
###################### End Of Configuration ##########################
######################################################################


cards_per_page = rows * cols
page_size = (page_width * ppi, page_height * ppi)


class MembershipCardApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_path = "membership.db"

        self.image_path = None
        self.qr_size_input = None
        self.qr_x_position_input = None
        self.qr_y_position_input = None
        self.num_pages_input = None
        self.visualizer_label = None

        self.init_db()
        self.initUI()
        self.load_settings_from_db()



    def init_db(self):
        """Initialize the SQLite database and create necessary tables."""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS used_numbers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number INTEGER NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS qr_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                size REAL NOT NULL,
                x_position REAL NOT NULL,
                y_position REAL NOT NULL
            )
        ''')
        self.conn.commit()

    def load_settings_from_db(self):
        """Load saved QR code settings from the database."""
        self.cursor.execute('SELECT size, x_position, y_position FROM qr_settings WHERE id = 1')
        result = self.cursor.fetchone()
        if result:
            self.qr_size_input.setValue(result[0])
            self.qr_x_position_input.setValue(result[1])
            self.qr_y_position_input.setValue(result[2])

    def generate_new_number(self):
        """Generate a unique random number for the QR code."""
        new_number = random.randint(1, 10000000)  # You can adjust the range as needed
        query = f"SELECT 1 FROM used_numbers WHERE number = '{new_number}'"
        self.cursor.execute(query)
        test = self.cursor.fetchone()
        if test is None:
            return new_number
        else:
            return self.generate_new_number()

    def save_settings_to_db(self):
        """Save the current QR code settings to the database."""
        size = self.qr_size_input.value()
        x_position = self.qr_x_position_input.value()
        y_position = self.qr_y_position_input.value()
        self.cursor.execute('''
            INSERT INTO qr_settings (id, size, x_position, y_position)
            VALUES (1, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
            size=excluded.size,
            x_position=excluded.x_position,
            y_position=excluded.y_position
        ''', (size, x_position, y_position))
        self.conn.commit()

    def add_number_to_database(self, number):
        """Add a generated number to the database."""
        self.cursor.execute(f'INSERT INTO used_numbers (number) VALUES ({number})')
        self.conn.commit()

    def initUI(self):
        """Initialize the user interface."""
        self.setWindowTitle('Generador de Membresias') # TRANSLATE
        self.setGeometry(100, 100, 500, 400) # (x, y, width, height)

        # Main layout
        main_layout = QVBoxLayout()

        # Form layout for settings
        form_layout = QFormLayout()

        # QR size input
        self.qr_size_input = QDoubleSpinBox()
        self.qr_size_input.setRange(0.1, 10.0)
        self.qr_size_input.setValue(2.0)
        self.qr_size_input.setSuffix(" cm")
        self.qr_size_input.valueChanged.connect(self.update_settings)
        form_layout.addRow("Tamaño codigo QR:", self.qr_size_input) # TRANSLATE

        # QR x position input
        self.qr_x_position_input = QDoubleSpinBox()
        self.qr_x_position_input.setRange(0, 20)
        self.qr_x_position_input.setValue(1.0)
        self.qr_x_position_input.setSuffix(" cm")
        self.qr_x_position_input.valueChanged.connect(self.update_settings)
        form_layout.addRow("Codigo QR - Posición X:", self.qr_x_position_input) # TRANSLATE

        # QR y position input
        self.qr_y_position_input = QDoubleSpinBox()
        self.qr_y_position_input.setRange(0, 20)
        self.qr_y_position_input.setValue(1.0)
        self.qr_y_position_input.setSuffix(" cm")
        self.qr_y_position_input.valueChanged.connect(self.update_settings)
        form_layout.addRow("Codigo QR - Posición Y:", self.qr_y_position_input) # TRANSLATE

        # Number of pages input
        self.num_pages_input = QSpinBox()
        self.num_pages_input.setRange(1, 10000)
        self.num_pages_input.setValue(1)
        form_layout.addRow("Numero de hojas:", self.num_pages_input) # TRANSLATE


        # Select Image button
        select_image_button = QPushButton("Seleccionar Imagen") # TRANSLATE
        select_image_button.clicked.connect(self.select_image)
        main_layout.addWidget(select_image_button)

        main_layout.addLayout(form_layout)

        # Generate button
        generate_button = QPushButton("Generar Membresias") # TRANSLATE
        generate_button.clicked.connect(self.generate_membership_cards)
        main_layout.addWidget(generate_button)
        
        main_layout.addStretch()

        # Visualizer label
        self.visualizer_label = QLabel()
        self.visualizer_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.visualizer_label)

        main_layout.addStretch()


        # Container widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def update_settings(self):
        """Update settings in the database and refresh the visualizer."""
        self.save_settings_to_db()
        self.update_visualizer()

    def select_image(self):
        """Open a file dialog to select the background image."""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Seleccionar Imagen de Fondo", "", "Images (*.png *.jpg *.bmp)", options=options) # TRANSLATE
        if file_name:
            self.image_path = file_name
            self.update_visualizer()

    def update_visualizer(self):
        """Update the visualizer to show the QR code on the selected background image."""
        if hasattr(self, 'image_path'):
            qr_size = self.qr_size_input.value()
            qr_x_position = self.qr_x_position_input.value()
            qr_y_position = self.qr_y_position_input.value()
            
            cm_to_points = ppi/2.54 # 1 inch = 2.54 cm, we use that number to get how many points are in 1 cm by dividing ppi/1"

            qr_img = self.generate_qr_code("Sample QR", int(qr_size * cm_to_points)) # Generate a sample qrcode image
            bg_img = Image.open(self.image_path) # Open the background image
            bg_img = bg_img.resize((int(card_width_cm * cm_to_points), int(card_height_cm * cm_to_points))) # resize the image to the specified dimensions

            # Set the position of the qrcode
            qr_x_pos = int(qr_x_position * cm_to_points)
            qr_y_pos = int(qr_y_position * cm_to_points)
            # Place the qrcode on top of the image
            bg_img.paste(qr_img, (qr_x_pos, qr_y_pos))
            # Background image configuration
            bg_img = bg_img.convert("RGBA")
            data = bg_img.tobytes("raw", "RGBA")
            qim = QImage(data, bg_img.size[0], bg_img.size[1], QImage.Format_RGBA8888)
            pixmap = QPixmap.fromImage(qim)
            # 400 and 500 are just random values for the visualizer, they can be changed and it doesn't affect much.
            self.visualizer_label.setPixmap(pixmap.scaled(400, 500, Qt.KeepAspectRatio))

    def generate_qr_code(self, data, qr_size):
        """Generate a QR code with the given data and size."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        img = img.resize((qr_size, qr_size))
        return img

    def generate_membership_cards(self):
        """Generate the PDF with the membership cards."""
        if not hasattr(self, 'image_path'):
            return # Do nothing if no image is selected

        resol = ppi / 2.54 # Setup the resolution for the document

        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_pdf = f"Membresias_{now}.pdf" # TRANSLATE

        image_path = self.image_path
        qr_size_cm = self.qr_size_input.value()
        qr_position = (self.qr_x_position_input.value(), self.qr_y_position_input.value())
        num_pages = self.num_pages_input.value()


        c = canvas.Canvas(output_pdf, pagesize=orientation(page_size))
        page_width, page_height = orientation(page_size)


        # Calculate the drawing area size and position
        drawing_width = card_width_cm * cols * resol
        drawing_height = card_height_cm * rows * resol
                
        start_x = (page_width - drawing_width) / 2
        start_y = (page_height - drawing_height) / 2

        for page in range(num_pages):
            for index in range(cards_per_page):
                row = index // cols
                col = index % cols
                if row >= rows:
                    break

                # Generate a unique number for the QR code
                qr_data = str(self.generate_new_number())
                self.add_number_to_database(qr_data)

                # Position for this card
                x = start_x + col * card_width_cm * resol
                y = start_y + (rows - row - 1) * card_height_cm * resol

                # Draw the background image on the card
                c.drawImage(image_path, x, y, width=card_width_cm * resol, height=card_height_cm * resol)

                # Generate QR code and convert it to an ImageReader object
                qr_size = qr_size_cm * resol
                qr_img = self.generate_qr_code(qr_data, int(qr_size))
                buffer = BytesIO()
                qr_img.save(buffer, format='PNG')
                buffer.seek(0)
                qr_img_reader = ImageReader(buffer)

                # Convert QR code position from top-left (UI) to bottom-left (PDF)
                # We do this because the library for the UI and for the PDF creator take different coordinates.
                qr_x_cm, qr_y_cm = qr_position
                qr_x = x + qr_x_cm * resol
                qr_y = y + card_height_cm * resol - (qr_y_cm * resol + qr_size)

                c.drawImage(qr_img_reader, qr_x, qr_y, width=qr_size, height=qr_size)

            c.showPage()  # Add a new page

        c.save()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MembershipCardApp()
    ex.show()
    sys.exit(app.exec_())
