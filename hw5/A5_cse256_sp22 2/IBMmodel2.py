from collections import Counter, defaultdict
import pickle

class Ibmmodel_2:
    def __init__(self,ibm1_path) -> None:
        self.ibm1_path = ibm1_path
    
    def get_corpus(self, english_corpu, spanish_corpus):
        with open(self.ibm1_path, 'rb') as ibm1_file:
            self.t = pickle.load(ibm1_file)
        print('Loaded ibm1_file.')
        en_file = open(english_corpu)
        sp_file = open(spanish_corpus)
        self.english_tokens = []
        self.spanish_tokens = []
        self.word = Counter()

        for line in en_file:
            token = ['_NULL_'] + line.rstrip().split()
            self.word += Counter(token)
            self.english_tokens.append(token)
        
        for line2 in sp_file:
            token_2 = line2.rstrip().split()
            self.spanish_tokens.append(token_2)
        return  self.t, self.word, self.english_tokens, self.spanish_tokens
        
    def train_model(self, iters, english_corpu, spanish_corpus):
        self.q = {}
        self.t ,self.word,b,c = self.get_corpus(english_corpu, spanish_corpus)
        for iter in range(iters):
            c_pair = defaultdict(int)
            c_eng = defaultdict(int)
            c_jilm = defaultdict(int)
            c_ilm = defaultdict(int)
            en_file = open(english_corpu)
            es_file = open(spanish_corpus)
            print('iter:', iter+1)
            for en_line, es_line in zip(en_file, es_file):
                eng_tok = ['_NULL_'] + en_line.rstrip().split()
                spn_tok = es_line.rstrip().split()
                l = len(spn_tok)
                m = len(eng_tok)
                for i in range(l):
                    t_sum = 0
                    for j in range(m):
                        t_sum += self.q.get((j, i, l, m), 1.0/(l+1)) * self.t.get((spn_tok[i], eng_tok[j]), 1.0/self.word[eng_tok[j]])
        #             t_sum = self._sum(eng_tok, spn_tok, i)
                    for j in range(m):
                        en, es = eng_tok[j], spn_tok[i]
                        t= self.q.get((j, i, l, m), 1.0/(l+1)) * self.t.get((es, en), 1.0 / self.word[en])
                        delta = float(t) / t_sum
                        c_pair[(en, es)] = c_pair.get((en, es), 0.0) + delta
                        c_eng[en] = c_eng.get(en, 0) + delta
                        c_jilm[(j, i, l, m)] = c_jilm.get((j, i, l, m), 0.0) + delta
                        c_ilm[(i,l,m)] = c_ilm.get((i,l,m), 0.0) + delta

            for (en, es), score in c_pair.items():
                self.t[(es, en)] = float(score) / c_eng[en]
            
            for (j, i, l, m), e_score in c_jilm.items():
                self.q[(j, i, l, m)] = float(e_score) / c_ilm[(i,l,m)]
        print(self.q)
    

    def predict_position(self, english_corpu, spanish_corpus, out_file):
        # p, a, self.english_tokens, self.spanish_tokens = self.get_corpus(english_corpu, spanish_corpus)
        # print(len(self.english_tokens))
        # print(len(self.spanish_tokens))
        en_file = open(english_corpu)
        es_file = open(spanish_corpus)
        # aral_file = zip(self.english_tokens, self.spanish_tokens)
        # print(paral_file[1])p
        # zipfile = zip(en_file, es_file)
        with open(out_file, 'w') as out_result:
            idx = 0
            for en_line, es_line in zip(en_file, es_file):
                en_line = '_NULL_ ' + en_line
                en_tokens = en_line.rstrip().split()
                es_tokens = es_line.rstrip().split()
                l = len(es_tokens)
                m = len(en_tokens)
                for i in range(l):
                    max_j = 0
                    max_score = 0
                    for j in range(m):
                        eng, espan = en_tokens[j], es_tokens[i]
                        if self.q.get((j, i, l, m), 0) * self.t.get((espan,eng),0) > max_score:
                            max_score = self.q.get((j, i, l, m), 0) * self.t.get((espan,eng),0)
                            max_j = j

                    out_result.write('%d %d %d\r\n' %(idx+1, max_j, i+1))
                idx += 1
                


if __name__ == '__main__':
    ibm2 = Ibmmodel_2('ibm_model1_t.pkl')
    ibm2.train_model(5, 'corpus.en', 'corpus.es')
    ibm2.predict_position('dev.en', 'dev.es','alignment.p2.out')







                    






