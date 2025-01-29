#!/bin/bash
set -e  # Stop script on first error

# Update package lists
apt-get update 

# Install Tesseract OCR and necessary language data
apt-get install -y tesseract-ocr tesseract-ocr-eng

# Show installation path of Tesseract
which tesseract

# Show Tesseract version to confirm installation
tesseract --version
