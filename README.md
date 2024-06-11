# QrCards

## Membership Card Generator

This Python application generates membership cards with embedded QR codes. It provides a graphical user interface (GUI) to customize the size and position of the QR codes on the cards and allows saving these settings to a SQLite database. The final output is a PDF containing the membership cards.

## Features

    Generate Unique QR Codes: Ensures that each membership card has a unique QR code.
    Customizable QR Code Settings: Allows users to set the size and position of the QR code on the card.
    GUI for Easy Interaction: Utilizes PyQt5 for a user-friendly interface to set parameters and generate cards.
    PDF Output: Generates a PDF document with the specified number of membership cards.
    SQLite Database Integration: Saves and retrieves settings and used numbers from a SQLite database.

## Requirements

    Python 3.x
    PyQt5
    qrcode
    Pillow (PIL)
    reportlab


## Usage

    python QrCards.py

    Application Interface:
        Select Image: Choose the background image for the membership cards.
        Set QR Code Size: Adjust the size of the QR code (in cm).
        Set QR Code Position: Set the X and Y positions of the QR code on the card.
        Number of Pages: Define the number of pages of membership cards to generate.
        Generate Membership Cards: Click to generate the PDF with the membership cards.

    Generated PDF:
        The application will create a PDF file named cards.pdf containing the specified number of membership cards.

## Code Overview
### Main Components

    MembershipCardApp: The main window class that initializes the GUI and handles user interactions.
    Database Initialization: Creates tables for storing used numbers and QR code settings.
    QR Code Generation: Generates unique QR codes and ensures no duplicates.
    PDF Generation: Generates the PDF file with the membership cards.

### Key Functions

    init_db(): Initializes the database and creates necessary tables.
    load_settings_from_db(): Loads saved QR code settings from the database.
    save_settings_to_db(): Saves current QR code settings to the database.
    generate_new_number(): Generates a unique number for the QR code.
    add_number_to_database(): Adds a generated number to the database.
    generate_qr_code(): Creates a QR code image.
    generate_membership_cards(): Generates the PDF with membership cards.

## Contributing

Contributions are welcome! Please create an issue or submit a pull request with your changes.

## License

This project is licensed under the "GNU LGPL Version 2.1". See the LICENSE file for details.