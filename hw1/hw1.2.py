#!/bin/python
from nltk.tokenize.regexp import regexp_tokenize
import re
Word = re.compile(r'\w+')
def read_tsv(tar, fname):
    member = tar.getmember(fname)
    print(member.name)
    tf = tar.extractfile(member)
    data = []
    labels = []
    for line in tf:
        line = line.decode("utf-8")
        (label,text) = line.strip().split("\t")
        labels.append(label)
        data.append(text)
    return data, labels
def read_files(tarfname, T):
    """Read the training and development data from the sentiment tar file.
    The returned object contains various fields that store sentiment data, such as:

    train_data,dev_data: array of documents (array of words)
    train_fnames,dev_fnames: list of filenames of the doccuments (same length as data)
    train_labels,dev_labels: the true string label for each document (same length as data)

    The data is also preprocessed for use with scikit-learn, as:

    count_vec: CountVectorizer used to process the data (for reapplication on new data)
    trainX,devX: array of vectors representing Bags of Words, i.e. documents processed through the vectorizer
    le: LabelEncoder, i.e. a mapper from string labels to ints (stored for reapplication)
    target_labels: List of labels (same order as used in le)
    trainy,devy: array of int labels, one for each document
    """
    import tarfile
    tar = tarfile.open(tarfname, "r:gz")
    trainname = "train.tsv"
    devname = "dev.tsv"
    for member in tar.getmembers():
        if 'train.tsv' in member.name:
            trainname = member.name
        elif 'dev.tsv' in member.name:
            devname = member.name
            
            
    class Data: pass
    sentiment = Data()
    # print("-- train data")
    sentiment.train_data, sentiment.train_labels = read_tsv(tar,trainname)
    # print(len(sentiment.train_data))

    # print("-- dev data")
    sentiment.dev_data, sentiment.dev_labels = read_tsv(tar, devname)
    # print(len(sentiment.dev_data))
    # print("-- transforming data and labels")
    from sklearn.feature_extraction.text import CountVectorizer
    sentiment.count_vect = CountVectorizer(tokenizer=T)
    sentiment.trainX = sentiment.count_vect.fit_transform(sentiment.train_data)
    sentiment.devX = sentiment.count_vect.transform(sentiment.dev_data)
    from sklearn import preprocessing
    sentiment.le = preprocessing.LabelEncoder()
    sentiment.le.fit(sentiment.train_labels)
    sentiment.target_labels = sentiment.le.classes_
    sentiment.trainy = sentiment.le.transform(sentiment.train_labels)
    sentiment.devy = sentiment.le.transform(sentiment.dev_labels)
    tar.close()
    return sentiment


def clean(word):
    word = word.replace("\n", " ").replace("\r", " ")
    punc_list = '!"#$%&*()+_,.:;<=>?@[]\^_{|}~' +'0123456789'
    t = str.maketrans(dict.fromkeys(punc_list, " "))
    word = word.translate(t)

    t = str.maketrans(dict.fromkeys("'`", ""))
    word = word.translate(t)
    return word


def my_token(word): 
    word = clean(word)   
    words = regexp_tokenize(word, pattern='\s+', gaps=True)
    return words

def my_token2(word): 
    words = regexp_tokenize(word, pattern='\s+', gaps=True)
    return words


if __name__ == "__main__":
    import classify
    tarfname = "data/sentiment.tar.gz"
    for T in [None, my_token, my_token2]:
        sentiment = read_files(tarfname, T)
        cls = classify.train_classifier(sentiment.trainX, sentiment.trainy)
        print("my_token is %s" % T)
        classify.evaluate(sentiment.trainX, sentiment.trainy, cls, 'train')
        classify.evaluate(sentiment.devX, sentiment.devy, cls, 'dev')


