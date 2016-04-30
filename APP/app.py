from flask import Flask

from flask import (request,
                   redirect,
                   url_for,
                   session,
                   render_template)

from collections import deque, defaultdict
import cPickle as pickle
import pandas as pd
import pymongo
from pymongo import MongoClient
from sklearn.metrics.pairwise import linear_kernel
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import jaccard_similarity_score
import numpy as np
import pandas as pd
import re
import json
import logging
import random
import pymongo
import nltk.data
from itertools import chain
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
from scipy.spatial.distance import cdist
from sklearn.metrics.pairwise import linear_kernel
from pymongo import MongoClient
from random import sample
import statsmodels.api as sm
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.metrics.pairwise import cosine_similarity


client = MongoClient()
db = client['tweets_db']
cursor = db.tweets.find()
count = 400000
tweets = []
for tweet in cursor:
    count -= 1
    try:
        if 'text' in tweet:
            td = {}
            td['text'] = tweet['text']
            td['hashtags'] = tweet['entities']['hashtags'][0]['text']
            td['timestamp'] = tweet['created_at']
            tweets.append(td)
    except:
        continue
    if count <= 0:
        break
df = pd.DataFrame(tweets)
print 'df', len(df)
tweet_list = []
for text in df['text'].values:
    text = re.sub(r"#|@|http\S+", "", text).lower()
    tweet_list.append(text)
docs = [word_tokenize(content) for content in tweet_list]
print 'docs', len(docs)
stop = set(stopwords.words('english'))
docs = [[word for word in words if word not in stop] for words in docs]
wordnet = WordNetLemmatizer()
docs_wordnet = [[wordnet.lemmatize(word) for word in words] for words in docs]
docs = docs_wordnet

docs_joined = [' '.join(x) for x in docs]
hv = HashingVectorizer(n_features=10000, non_negative=True)
docs_vectorized = hv.fit_transform(docs_joined).toarray()

def get_similar(tweet):
    docs2 = word_tokenize(tweet)
    docs2 = [word for word in docs2 if word not in stop]
    docs_wordnet2 = [wordnet.lemmatize(word) for word in docs2]
    docs2 = docs_wordnet2
    print docs2
    docs_joined2 = [' '.join(docs2)]
    print docs_joined2
    docs_vectorized2 = hv.transform(docs_joined2).toarray()
    sorted_similar_tweets = np.argsort(cdist(docs_vectorized2[0, :][np.newaxis, :], docs_vectorized, 'jaccard'))
    return sorted_similar_tweets

# vectorized_tweets.update(new_tweet)

# BEGIN APP

app = Flask(__name__)

# home page
@app.route('/')
def welcome():
    return render_template('index.html')

@app.route('/submit', methods=['POST'] )
def submission_page():
    tweet = str(request.form['newtext'])

    page = 'The path is : {0} '
    sorted_similar_tweets = get_similar(tweet)
    print sorted_similar_tweets.shape
    print len(docs_vectorized)
    return tweet_list[sorted_similar_tweets[0][0]]

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
