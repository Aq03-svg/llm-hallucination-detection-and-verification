import re
from typing import List, Dict, Tuple
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class TextProcessor:
    """Utilities for text processing and analysis."""
    
    @staticmethod
    def tokenize_sentences(text: str) -> List[str]:
        """Split text into sentences."""
        return sent_tokenize(text)
    
    @staticmethod
    def tokenize_words(text: str) -> List[str]:
        """Split text into words."""
        return word_tokenize(text.lower())
    
    @staticmethod
    def remove_stopwords(words: List[str], language: str = 'english') -> List[str]:
        """Remove common stopwords."""
        stop_words = set(stopwords.words(language))
        return [word for word in words if word.lower() not in stop_words]
    
    @staticmethod
    def extract_entities(text: str) -> Dict[str, List[str]]:
        """Extract named entities from text."""
        # Simple pattern-based entity extraction
        entities = {
            'person': [],
            'location': [],
            'organization': [],
            'date': [],
            'number': []
        }
        
        # Date patterns
        date_pattern = r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}|\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{2}-\d{2}'
        entities['date'] = re.findall(date_pattern, text)
        
        # Number patterns
        number_pattern = r'\b\d+(?:,\d{3})*(?:\.\d+)?\b'
        entities['number'] = re.findall(number_pattern, text)
        
        return entities
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,:;!?()\-]', '', text)
        return text
    
    @staticmethod
    def extract_clauses(sentence: str) -> List[str]:
        """Extract independent and dependent clauses from a sentence."""
        # Simple clause extraction based on conjunctions
        conjunctions = ['and', 'but', 'or', 'yet', 'so', 'because', 'although', 'if', 'when', 'while']
        clauses = [sentence]
        
        for conj in conjunctions:
            pattern = f'\\b{conj}\\b'
            parts = re.split(pattern, sentence, flags=re.IGNORECASE)
            if len(parts) > 1:
                clauses = parts
                break
        
        return [clause.strip() for clause in clauses if clause.strip()]
    
    @staticmethod
    def get_text_statistics(text: str) -> Dict[str, int]:
        """Calculate basic text statistics."""
        sentences = TextProcessor.tokenize_sentences(text)
        words = TextProcessor.tokenize_words(text)
        
        return {
            'character_count': len(text),
            'word_count': len(words),
            'sentence_count': len(sentences),
            'average_word_length': len(text) / len(words) if words else 0,
            'average_sentence_length': len(words) / len(sentences) if sentences else 0
        }
