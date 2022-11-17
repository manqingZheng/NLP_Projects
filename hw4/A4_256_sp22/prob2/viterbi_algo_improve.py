from asyncio.constants import LOG_THRESHOLD_FOR_CONNLOST_WRITES
import re
import sys
from collections import defaultdict
import math
import itertools
from replace_rare_improve import rare_classifier

def count_tags(corpus_file, dict_emission, dict_n_gram, dict_word):
    for l in corpus_file:
        line = l.strip().split(' ')
        if line[1] == 'WORDTAG':
            dict_emission[(line[2], line[3])] = int(line[0])
            dict_word[line[3]] += 1
        else:
            dict_n_gram[tuple(line[2:])] = int(line[0])

def viterbi_algo(list_word, dict_n_gram, dict_word, dict_emission):
    tag_set = ('O', 'I-GENE')
    bp_dict = defaultdict()
    pi_dict = {(1, '*', '*'): 1}
    list_word = ['*','*'] + list_word
    for k in range(2, len(list_word)):
        if k == 2:
            U = ('*', )
            W = ('*', )
            V = tag_set
        elif k == 3:
            W = ('*', )
            U = tag_set
            V = tag_set
        else: 
            U, V, W = tag_set, tag_set, tag_set
        
        for u, v in itertools.product(U, V):
            x = list_word[k] if list_word[k] in dict_word else rare_classifier(list_word[k])
            e =  float(dict_emission[(v, x)]) / float(dict_n_gram[(v,)]) 
            pi_list = [((pi_dict[k-1, w, u] * (dict_n_gram[w,u,v]/ float(dict_n_gram[w,u])) * e), w) for w in W]
            pi_dict[k,u,v], bp_dict[k,u,v] = max(pi_list, key = lambda x: x[0])

    v_u_list = [(pi_dict[len(list_word) - 1, u, v] * (dict_n_gram[u,v,'STOP']/ dict_n_gram[u,v]), (u,v)) for 
                (u,v) in itertools.product(tag_set, tag_set) ]
    tag_u, tag_v = max(v_u_list, key = lambda x: x[0])[1]
    tag = [0] * len(list_word)
    tag[-1], tag[-2] = tag_v, tag_u
    for k in reversed(range(len(list_word)-2)):
        tag[k] = bp_dict[k+2, tag[k+1], tag[k+2]]
    return tag[2:]




def write_to_genefile(corpus_file, output_file, dict_n_gram, dict_word, dict_emission):
    list_word = []
    for l in corpus_file:
        line = l.strip()
        if line:
            list_word.append(line)
        else:
            list_tag = viterbi_algo(list_word, dict_n_gram, dict_word, dict_emission)
            for i, word in enumerate(list_word):
                output_file.write("%s %s\n" % (word, list_tag[i]))
            output_file.write("\n")
            list_word = []
    output_file.close()


if __name__ == "__main__":

    if len(sys.argv)!=3:  # Expect exactly one argument: the training data file
        sys.exit(2)

    try:
        input = open(sys.argv[1],"r")
        input2 = open(sys.argv[2], "r")
    except IOError:
        sys.stderr.write("ERROR: Cannot read inputfile %s.\n" % arg)
        sys.exit(1)

    dict_emission, dict_n_gram, dict_word = defaultdict(int), defaultdict(int),defaultdict(int)
    count_tags(input,dict_emission, dict_n_gram, dict_word)
    input.close()
    write_to_genefile(input2,sys.stdout, dict_n_gram, dict_word, dict_emission)
    input2.close()



