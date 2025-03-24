# **Check Splitter**

Check Splitter is a web application built to help users effortlessly split a restaurant bill based on the items they ordered. The app uses OCR (Optical Character Recognition) technology to scan and extract details from an image of a restaurant check, and then it calculates the split between different users. This project utilizes pytesseract for OCR image processing, and it is hosted on Heroku.

## **Project Status**
This project is functional, but this is the first version. I have updated this application and it is published under Check-Splitter Enhanced, check it out!

## **Project Screen Shots**

![Screenshot 2025-02-12 133632](https://github.com/user-attachments/assets/f623a9ea-5907-4211-a3e3-a7d502c47530)  
<img width="704" alt="image" src="https://github.com/user-attachments/assets/5538d78a-40c2-417a-b20e-727593c391c2" />

<img width="1279" alt="image" src="https://github.com/user-attachments/assets/b9ece653-fad6-492c-9d35-1ddfc3d61008" />  
<img width="1279" alt="image" src="https://github.com/user-attachments/assets/c50f1ae5-473f-43b1-83ba-097d8eaf02af" />

## **Installation and Setup Instructions**
To set up this project locally, you will need to clone the repository and install the necessary dependencies. Follow the steps below to get started.

### **Installation:**

1. Clone this repository to your local machine:
   ```
   git clone https://github.com/yourusername/check-splitter.git
   ```
2. Navigate into the project directory:
   ```
   cd check-splitter
   ```
3. Set up a virtual environment (optional, but recommended):
   ```
   python -m venv venv
   ```
4. Activate the virtual environment:
- On Windows:
  ```
  .\venv\Scripts\activate
  ```
- On MacOS/Linux:
  ```
  source venv/bin/activate
  ```

5. Install the dependencies listed in requirements.txt:
  ```
   pip install -r requirements.txt
  ```
6. Set up the Heroku app and deploy (if using Heroku):
- Ensure that you have the Heroku CLI installed.
- Run:
  ```
  heroku create check-splitter
  ```
  (You may skip this if you already created the Heroku app.)
- Push to Heroku:
  ```
  git push heroku main
  ```

7. For local testing, run the server:
```
   python app.py
```
   (Visit the specified link to use the app.)

## **Configuration**  
For Heroku, make sure to set the correct TESSDATA_PREFIX for pytesseract to work correctly: 
```
heroku config:set TESSDATA_PREFIX=/app/.apt/usr/share/tesseract-ocr/5/tessdata -a check-splitter
```


## **Reflection**

### What was the context for this project?
This project was built as a side project to implement OCR technology in a practical scenario. I wanted to create something useful that helps people easily split restaurant bills without manually entering the details.

### What did you set out to build?
I set out to build a web application that could use OCR to extract restaurant check details and then split the bill between users based on what they ordered. The goal was to integrate pytesseract for image recognition and create an easy-to-use interface.

### Why was this project challenging and a good learning experience?
The most challenging part of this project was ensuring the OCR technology could accurately read and parse restaurant checks, which can vary greatly in format. Understanding how to extract the correct data from a variety of check types was an interesting problem to solve. Additionally, configuring Heroku to work with pytesseract (and related dependencies) required some troubleshooting and learning.

### What were some unexpected obstacles?
- Getting Heroku to properly configure and install the Tesseract OCR engine was a bit tricky. There were issues with setting the TESSDATA_PREFIX variable and making sure the app correctly referenced the correct installation path for tesseract-ocr.
- Handling different styles of restaurant checks (fonts, layouts, etc.) required some time to fine-tune the image processing.

### What tools did you use to implement this project?
- Python: The main programming language for the app.
- Flask: The web framework used to create the backend of the app.
- pytesseract: The Python library used for OCR to extract text from the check images.
- Heroku: Used for hosting the web app.
- HTML/CSS: Used for the frontend of the web application.
- JavaScript: For basic interactivity on the frontend.

### Why did you choose these tools?
- I chose Flask because it's a lightweight framework that was easy to set up and allowed me to focus on building out the core functionality of the app. I used pytesseract because it provides a simple interface to Tesseract OCR, which is the go-to open-source OCR engine. The decision to use Heroku was based on its ease of deployment for web apps, and it helped me quickly get the app online for testing and production use.  
- For the frontend, I kept things simple with HTML and CSS, while also incorporating JavaScript for interactive elements.  
-  the future, I plan on exploring more advanced methods of handling OCR and refining the app’s user interface.





