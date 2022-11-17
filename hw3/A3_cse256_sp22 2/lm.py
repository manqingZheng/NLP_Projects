#!/bin/python

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from calendar import c

import collections
from math import log
import sys
from tqdm import tqdm

# Python 3 backwards compatibility tricks
if sys.version_info.major > 2:

    def xrange(*args, **kwargs):
        return iter(range(*args, **kwargs))

    def unicode(*args, **kwargs):
        return str(*args, **kwargs)

class LangModel:
    def fit_corpus(self, corpus):
        """Learn the language model for the whole corpus.

        The corpus consists of a list of sentences."""
        for s in corpus:
            self.fit_sentence(s)
        self.norm()

    def perplexity(self, corpus):
        """Computes the perplexity of the corpus by the model.

        Assumes the model uses an EOS symbol at the end of each sentence.
        """
        return pow(2.0, self.entropy(corpus))

    def entropy(self, corpus):
        num_words = 0.0
        sum_logprob = 0.0
        for s in corpus:
            num_words += len(s) + 1 # for EOS
            sum_logprob += self.logprob_sentence(s)
        return -(1.0/num_words)*(sum_logprob)

    def logprob_sentence(self, sentence):
        p = 0.0
        for i in xrange(len(sentence)):
            p += self.cond_logprob(sentence[i], sentence[:i])
        p += self.cond_logprob('END_OF_SENTENCE', sentence)
        return p

    # required, update the model when a sentence is observed
    def fit_sentence(self, sentence): pass
    # optional, if there are any post-training steps (such as normalizing probabilities)
    def norm(self): pass
    # required, return the log2 of the conditional prob of word, given previous words
    def cond_logprob(self, word, previous): pass
    # required, the list of words the language model suports (including EOS)
    def vocab(self): pass

class Unigram(LangModel):
    def __init__(self, backoff = 0.000001):
        self.model = dict()
        self.lbackoff = log(backoff, 2)

    def inc_word(self, w):
        if w in self.model:
            self.model[w] += 1.0
        else:
            self.model[w] = 1.0

    def fit_sentence(self, sentence):
        for w in sentence:
            self.inc_word(w)
        self.inc_word('END_OF_SENTENCE')

    def norm(self):
        """Normalize and convert to log2-probs."""
        tot = 0.0
        for word in self.model:
            tot += self.model[word]
        ltot = log(tot, 2)
        for word in self.model:
            self.model[word] = log(self.model[word], 2) - ltot

    def cond_logprob(self, word, previous):
        if word in self.model:
            return self.model[word]
        else:
            return self.lbackoff

    def vocab(self):
        return self.model.keys()

class Trigram(LangModel):
    def __init__(self, backoff = 0.000001, delta=0.01, smoothing='True', para2 = 4):
        self.model = dict()
        self.lbackoff = log(backoff, 2)
        self.unigram_model = dict()
        self.delta = delta
        self.para2 = para2
        self.smoothing = smoothing

    def inc_word(self, w):
        if w in self.unigram_model:
            self.unigram_model[w] += 1.0
        else:
            self.unigram_model[w] = 1.0
        # print('mm',len(self.unigram_model))
    
    def inc_2and3_words(self, w):
        if tuple(w) in self.model:
            self.model[tuple(w)] += 1.0
        else:
            self.model[tuple(w)] = 1.0
    
    def find_oov(self, corpus):
        unk = collections.defaultdict()
        for sentence in corpus:
            sentence=['*','*']+sentence+['END_OF_SENTENCE']
            for w in range(len(sentence)):
                self.inc_word(sentence[w])
        print('len1',len(self.unigram_model))
        for key in self.unigram_model.keys():
            if self.unigram_model[key] < self.para2:
                unk[key] = 1
        print('len',len(unk))
        
        n_corpus = corpus.copy()
        for sentence in tqdm(n_corpus):
            for w in range(len(sentence)):
                if sentence[w] in unk.keys():
                    sentence[w] ='UNK'
        return n_corpus
            
    def fit_corpus(self, corpus):
        n_corpus = self.find_oov(corpus)
        self.unigram_model = dict()
        for sentence in n_corpus:
            self.fit_sentence(sentence)



    def fit_sentence(self, sentence):
        sentence=['*','*']+sentence+['END_OF_SENTENCE']
        for i in range(len(sentence)):
            self.inc_word(sentence[i])
        for i in range(len(sentence)-2):
            self.inc_2and3_words((sentence[i:i+3]))
        for i in range(len(sentence)-1):
            self.inc_2and3_words((sentence[i:i+2]))

    def norm(self):
        """Normalize and convert to log2-probs."""
        tot = 0.0
        for word in self.model:
            tot += self.model[word]
        ltot = log(tot, 2)
        for word in self.model:
            self.model[word] = log(self.model[word], 2) - ltot

    def cond_logprob(self, word, previous):
        if self.smoothing == 'True':
            con_trigram = tuple(previous[-2:]+[word])
            con_bigram = tuple(previous[-1:]+[word])
            if con_trigram in self.model:
                cond_prob = (self.model[con_trigram]+self.delta)/(self.model[con_bigram]+(self.delta*len(self.vocab())))
                log_prob = log(cond_prob, 2)
                return log_prob
            else:
                return - log(len(self.vocab()), 2)
        else:
            con_trigram = tuple(previous[-2:]+[word])
            con_bigram = tuple(previous[-1:]+[word])
            if con_trigram in self.model:
                cond_prob = (self.model[con_trigram]+1)/(self.model[con_bigram]+len(self.vocab()))
                log_prob = log(cond_prob, 2)
                return log_prob
            else:
                return self.lbackoff

    def logprob_sentence(self, sentence):
        p = 0.0       
        for i in xrange(len(sentence)):
            p += self.cond_logprob(sentence[i], sentence[:i])
        p += self.cond_logprob('END_OF_SENTENCE', sentence)
        return p


    def vocab(self):
        return self.unigram_model.keys()
    
    def remove_oov(self, corpus):
        for s in corpus:
            for i in range(len(s)):
                if s[i] not in self.unigram_model:
                    s[i] = 'UNK'


    def perplexity(self, corpus):
        """Computes the perplexity of the corpus by the model.

        Assumes the model uses an EOS symbol at the end of each sentence.
        """
        self.remove_oov(corpus)
        return pow(2.0, self.entropy(corpus))
    

    

