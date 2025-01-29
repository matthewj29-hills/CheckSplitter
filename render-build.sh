#!/bin/bash
# Update package lists
apt-get update 

# Install Tesseract OCR and English language pack
apt-get install -y tesseract-ocr tesseract-ocr-eng 

# Print Tesseract version to confirm installation
tesseract --version

# Show where Tesseract is installed
which tesseract
