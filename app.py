from flask import Flask,request,render_template,url_for,jsonify
from flask_cors import CORS
import site
import numpy as np
import pandas as pd
import nltk
import re
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize,word_tokenize
from gensim.models import Word2Vec
from keras.layers import Embedding, LSTM, Dense, Dropout, Lambda, Flatten
from keras.models import Sequential, load_model, model_from_config
import keras.backend as K
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.metrics import cohen_kappa_score
from gensim.models.keyedvectors import KeyedVectors
from keras import backend as K


def sent2word(x):
    stop_words = set(stopwords.words('english')) 
    x = re.sub("[^A-Za-z]"," ",x)
    x.lower()
    filtered_sentence = [] 
    words = x.split()
    for w in words:
        if w not in stop_words: 
            filtered_sentence.append(w)
    return filtered_sentence



def essay2word(essay):
    essay = essay.strip()
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    raw = tokenizer.tokenize(essay)
    final_words = []
    for i in raw:
        if(len(i)>0):
            final_words.append(sent2word(i))
    return final_words

def makeVec(words, model, num_features):
    vec = np.zeros((num_features,),dtype = "float32")
    noOfWords = 0.
    index2word_set = set(model.index_to_key)
    for i in words:
        if i in index2word_set:
            noOfWords += 1
            vec = np.add(vec,model[i])        
    vec = np.divide(vec,noOfWords)
    return vec


def getVecs(essays, model, num_features):
    c = 0
    essay_vecs = np.zeros((len(essays),num_features),dtype = "float32")
    for i in essays:
        essay_vecs[c] = makeVec(i, model, num_features)
        c += 1
    return essay_vecs


def get_model():
    model = Sequential()
    model.add(LSTM(300, dropout = 0.4, recurrent_dropout = 0.4, input_shape = [1, 300], return_sequences = True))
    model.add(LSTM(64, recurrent_dropout = 0.4))
    model.add(Dropout(0.5))
    model.add(Dense(1, activation = 'relu'))
    model.compile(loss = 'mean_squared_error', optimizer = 'rmsprop', metrics = ['mae'])
    model.summary()
    return model

def convertToVec(text):
    content = text
    if len(content) > 20:
        num_features = 300
        model = KeyedVectors.load_word2vec_format("word2vecmodel2.bin", binary = True)
        clean_test_essays = []
        clean_test_essays.append(sent2word(content))
        testDataVecs = getVecs(clean_test_essays, model, num_features )
        testDataVecs = np.array(testDataVecs)
        testDataVecs = np.reshape(testDataVecs, (testDataVecs.shape[0], 1, testDataVecs.shape[1]))

        lstm_model = load_model("final_lstm2.h5")
        preds = lstm_model.predict(testDataVecs)
        if len(content.split()) < 100:
            return str(0)
        return str(round(preds[0][0] * 0.6))

        
app = Flask(__name__)
CORS(app)

@app.route('/', methods = ['POST'])
def create_task():
    K.clear_session()
    final_text = request.get_json("text")["text"]
    score = convertToVec(final_text)
    K.clear_session()
    print(score)
    return jsonify({'score': score}), 201
    # return score

if __name__ == '__main__':
    app.run(debug = True)

"""
This should at least output something!!
if(!result){
    output.innerHTML = "Your grade is: 0/10";
}
else{
    output.innerHTML = "Your grade is: "+result.score+"/10"
}
"""

# if essays is < =  100 or > 1000 then say "Please enter a valid GRE essay between 100-1000."