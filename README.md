# PDF Summary Generator

This Flask web application allows users to upload a PDF document in Marathi language, extract its text, generates summary, keywords and translate the summary and keywords to English.

## Features

+ PDF Upload: Users can upload a PDF document containing Marathi text.
+ Text Extraction: The application extracts text from the uploaded PDF document.
+ Summary Generation: It generates a summary of the extracted text using the Summa library.
+ Keyword Extraction: It extracts keywords from the generated summary using the NLTK library.
+ Translation: Users can translate the summary and keywords from Marathi to English using the Google Translate API.
+ Web Interface: The application provides a user-friendly web interface for easy interaction.

## Prerequisites
+ Python 3.x
+ Flask
+ PyMuPDF (fitz)
+ googletrans
+ summa
+ spacy
+ nltk
