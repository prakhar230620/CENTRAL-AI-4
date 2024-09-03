import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from collections import Counter

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt_tab')

lemmatizer = WordNetLemmatizer()


def analyze_input(input_text):
    # Tokenization
    tokens = word_tokenize(input_text.lower())

    # Remove stopwords and punctuation
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word.isalnum() and word not in stop_words]

    # Lemmatization
    lemmatized_tokens = [lemmatizer.lemmatize(word) for word in filtered_tokens]

    # Keyword extraction (using frequency)
    keyword_freq = Counter(lemmatized_tokens)
    keywords = [word for word, freq in keyword_freq.most_common(5)]

    # Complexity calculation
    unique_words = set(lemmatized_tokens)
    complexity = len(unique_words) / len(lemmatized_tokens) if lemmatized_tokens else 0

    # Sentiment analysis (basic)
    positive_words = set(['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic'])
    negative_words = set(['bad', 'poor', 'terrible', 'awful', 'horrible', 'disgusting'])

    sentiment_score = sum(1 for word in lemmatized_tokens if word in positive_words) - \
                      sum(1 for word in lemmatized_tokens if word in negative_words)

    return {
        'keywords': keywords,
        'length': len(tokens),
        'complexity': complexity,
        'sentiment': sentiment_score,
        'question': any(word in ['what', 'why', 'how', 'when', 'where', 'who'] for word in tokens)
    }