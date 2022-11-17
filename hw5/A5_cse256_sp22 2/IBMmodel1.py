from collections import Counter, defaultdict
import pickle

class Ibmmodel_1:
    def __init__(self) -> None:
        pass
    
    def get_corpus(self, english_corpu, spanish_corpus):
        en_file = open(english_corpu)
        sp_file = open(spanish_corpus)
        self.word = Counter()
        self.english_tokens = []
        self.spanish_tokens = []

        for line in en_file:
            token = ['_NULL_'] + line.rstrip().split()
            self.word += Counter(token)
            self.english_tokens.append(token)
        
        for line2 in sp_file:
            token_2 = line2.rstrip().split()
            self.spanish_tokens.append(token_2)
        return  self.word, self.english_tokens, self.spanish_tokens
        
    def train_model(self, iters, english_corpu, spanish_corpus):
        self.t = {}
        # self.word, self.english_tokens, self.spanish_tokens = self.get_corpus(english_corpu, spanish_corpus)
        # paral_file = zip(self.english_tokens, self.spanish_tokens)
        self.word,b,c = self.get_corpus(english_corpu, spanish_corpus)
        for iter in range(iters):
            c_pair = defaultdict(int)
            c_eng = defaultdict(int)
            en_file = open(english_corpu)
            es_file = open(spanish_corpus)
            print('iter:', iter+1)
            for en_line, es_line in zip(en_file, es_file):
                eng_tok = ['_NULL_'] + en_line.rstrip().split()
                spn_tok = es_line.rstrip().split()
                for i in range(len(spn_tok)):
                    t_sum = 0
                    for j in range(len(eng_tok)):
                        t_sum += self.t.get((spn_tok[i], eng_tok[j]), 1.0/self.word[eng_tok[j]])
        #             t_sum = self._sum(eng_tok, spn_tok, i)
                    for j in range(len(eng_tok)):
                        en, es = eng_tok[j], spn_tok[i]
                        t= self.t.get((es, en), 1.0 / self.word[en])
                        delta = float(t) / t_sum
                        c_pair[(en, es)] = c_pair.get((en, es), 0.0) + delta
                        c_eng[en] = c_eng.get(en, 0) + delta

            for (en, es), score in c_pair.items():
                self.t[(es, en)] = float(score) / c_eng[en]
        # print(self.t)

    
    def save_t(self, save_path = 'ibm_model1_t'):
        with open(save_path, 'wb') as save_file:
            pickle.dump(self.t, save_file)
    

    def predict_position(self, english_corpu, spanish_corpus, out_file):
        a, self.english_tokens, self.spanish_tokens = self.get_corpus(english_corpu, spanish_corpus)
        res = []
        with open(out_file, 'w') as out_result:
            for idx in range(len(self.english_tokens)):
                for i in range(len(self.spanish_tokens[idx])):
                    max_j = 0
                    max_score = 0
                    for j in range(len(self.english_tokens[idx])):
                        eng, espan = self.english_tokens[idx][j], self.spanish_tokens[idx][i]
                        if self.t.get((espan,eng),0) > max_score:
                            max_score = self.t.get((espan,eng),0)
                            max_j = j

                    res.append(max_j)
                    out_result.write('%d %d %d\r\n' %(idx+1, max_j, i+1))
                
    
def load_parameter(load_path='ibm_model1_t.pkl'):
    with open(load_path, 'rb') as load_file:
        pickle.load(load_file)

if __name__ == '__main__':
    ibm1 = Ibmmodel_1()
    word = ibm1.train_model(5, 'corpus.en', 'corpus.es')
    ibm1.save_t('ibm_model1_t.pkl')
    # load_parameter()
    ibm1.predict_position('dev.en', 'dev.es','alignment.p1.out')







                    






