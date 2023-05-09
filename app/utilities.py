from nltk.tokenize import TweetTokenizer 
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from .models import ReviewScore

sentiment_analyzer = SentimentIntensityAnalyzer()
tweet_tokenizer = TweetTokenizer()
lemmatizer = WordNetLemmatizer()
tfidf_vectorizer = TfidfVectorizer(stop_words= stopwords.words('english'))

def preprocess_text(text: str) -> str:
	tokens = tweet_tokenizer.tokenize(text)
	lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens]

	tfidf_matrix = tfidf_vectorizer.fit_transform([' '.join(lemmatized_tokens)])
	tfidf_scores = dict(zip(tfidf_vectorizer.get_feature_names_out(), tfidf_matrix.toarray()[0]))

	sorted_tokens = sorted(tfidf_scores, key=tfidf_scores.get, reverse=True)

	return ' '.join(sorted_tokens[:10])

def get_sentiment_rating(text: str) -> ReviewScore:
	sentiment_scores = sentiment_analyzer.polarity_scores(preprocess_text(text))

	if sentiment_scores['compound'] > 0.05:
		return ReviewScore.POSITIVE
	elif sentiment_scores['compound'] < -0.05:
		return ReviewScore.NEGATIVE

	return ReviewScore.NEUTRAL
