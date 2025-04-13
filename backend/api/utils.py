import nltk
from textblob import TextBlob
import re

def download_nltk_data():
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
    
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')


def clean_text(text):
    """Nettoyer le texte pour l'analyse"""
    if not text:
        return ""
    
    text = text.lower()
    
    text = re.sub(r'https?://\S+|www\.\S+', '', text)    
    text = re.sub(r'<.*?>', '', text)    
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)    
    text = re.sub(r'\s+', ' ', text).strip()    
    return text


def analyze_sentiment(text):
    """
    Analyser le sentiment du texte et retourner un score
    entre -1.0 (très négatif) et 1.0 (très positif)
    """
    if not text:
        return 0.0
    
    clean = clean_text(text)
    if not clean:
        return 0.0
    
    blob = TextBlob(clean)    
    return blob.sentiment.polarity
