from flask import Flask, render_template, request ,flash
import fitz                             # for text extraction from PDF
import tempfile                         # for storing file in temp folder
import os
from googletrans import Translator      # For Translation the text
from summa import summarizer, keywords
import spacy
from nltk.tokenize import sent_tokenize, word_tokenize

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'secret key'

@app.route('/')
def index():
    return render_template('index.html')

import re
def is_marathi(text):
    marathi_pattern = re.compile(r'[\u0900-\u097F]+')
    return bool(marathi_pattern.search(text))

# Remove Stopwords
def remove_stopwords(text):
    nlp = spacy.blank("mr")
    doc1 = nlp(text)
    doc = str(doc1).split(' ')
    stopwords = nlp.Defaults.stop_words
    filtered_tokens = [token for token in doc if token not in stopwords]

    filtered_text = ' '.join(filtered_tokens)
    return filtered_text

# Extract Keywords
def extract_keywords(text):
    # Tokenize the text into words
    words = word_tokenize(text.lower())
    # Remove duplicates and return the list of unique words
    keywords = list(set(words))
    
    return keywords

translation_done = False

@app.route('/upload', methods=['POST'])
def upload():
    global translation_done
    global key_words
    if request.method == 'POST':
        file = request.files['file']
        temp_dir = tempfile.gettempdir()
        pdf_file = os.path.join(temp_dir, file.filename)
        file.save(pdf_file)
        translation_done = False
        
        try:
            pdf = fitz.open(pdf_file)
            page_count = pdf.page_count
            # text = pdf.load_page(10).get_text().replace("\n", ' ')    # For One page
            
            text = ""
            for page in range(page_count):
                page = pdf.load_page(page)
                extracted_text = page.get_text().replace("\n", ' ')
                if extracted_text != None:
                    text += (extracted_text)
            
            if page_count < 15:
                return "<h1>PDF must have 15 or more pages !!</h1>"
            if not is_marathi(text):
                return "<h1>PDF text must have in Marathi Language !!</h1>"
            
            else:
                # Generate summary
                summary = summarizer.summarize(text)
                
                pattern = r'(?<!\.)[^\u0900-\u097F\s.]|(?<=\.{2})\.'        # Remove unwated characters from text
                filtered_summary = re.sub(pattern,'',summary)
                
                # Extract keywords
                filter_words = remove_stopwords(filtered_summary)
                # key_words = keywords.keywords(filter_words split=True)   # Using SUMMA PY-Library
                key_words = extract_keywords(filter_words)                  # Using NLTK PY-Library
                    
                return render_template('result.html', count=page_count,page_content=text,summary=filtered_summary, key_words=key_words)
        except Exception as e:
            return f"<h1>Error: {e}</h1>"
    else:
        return 'Please upload a PDF file'

translator = Translator()
# translate Text
def translate_text(text):
    translated_text = translator.translate(text, src='mr', dest='en').text
    return translated_text

@app.route("/translate", methods=["GET"])
def translation():
    global translation_done
    translated_summary = ""
    translated_keywords = ""

    try:
        if not translation_done:
            marathi_text = request.args.get("text")
            marathi_keywords = request.args.get("keywords")
            
            pattern = r'(?<!\.)[^\u0900-\u097F\s.]|(?<=\.{2})\.'        # Remove unwated characters from text
            filtered_keywords = re.sub(pattern,'',marathi_keywords)
            
            # Text Translation
            translate_size = 5000
            for i in range(0,len(marathi_text),translate_size):
                size = marathi_text[i:i+translate_size]
                process_text = translate_text(size)
                translated_summary += process_text
                
            # Translate Keywords
            for i in range(0,len(filtered_keywords),translate_size):
                size = filtered_keywords[i:i+translate_size]
                process_text = translate_text(size)
                translated_keywords += process_text
            
            final_keywords = translated_keywords.split(" ")
            
            translation_done = True
            flash("Translation successful!", "success")
            return render_template('result.html', summary = translated_summary , key_words = final_keywords)
        else:
            return "Translation is already Done !!"
    except Exception as e:
        return f"<h1>Error: {e}</h1>"

if __name__ == '__main__':
    app.run(debug=True)