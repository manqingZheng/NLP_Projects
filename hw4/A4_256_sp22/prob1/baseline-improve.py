import re
import sys
from collections import defaultdict
import math
from replace_rare_improve import rare_classifier

def count_tags(corpus_file, dict_emission, dict_unigram, dict_word, dict_max_tag):
    for l in corpus_file:
        line = l.strip().split(' ')
        if line[1] == 'WORDTAG':
            dict_emission[(line[2], line[3])] = int(line[0])
            dict_word[line[3]] += 1
        elif line[1] == '1-GRAM':
            dict_unigram[line[2]] = int(line[0])

    for word in dict_word.keys():
        max_tag = ''
        max_v = -float('inf')
        for tag in dict_unigram.keys():
            e_eval = float(dict_emission[(tag, word)])/ float(dict_unigram[tag])
            if e_eval > max_v:
                max_v = e_eval
                max_tag = tag
        dict_max_tag[word] = max_tag

def write_to_genefile(corpus_file, dict_max_tag, output_file):
    for l in corpus_file:
        line = l.strip()
        if line:
            if line in dict_max_tag.keys():
                output_file.write("%s %s\n" % (line, dict_max_tag[line]))
            else:
                rare_word = rare_classifier(line)
                output_file.write("%s %s\n" % (line, dict_max_tag[rare_word]))
        else:
            output_file.write("\n")
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

    dict_emission, dict_unigram, dict_max_tag, dict_word = defaultdict(int), defaultdict(int),defaultdict(int),defaultdict(int)
    count_tags(input,dict_emission, dict_unigram, dict_word,dict_max_tag)
    input.close()
    write_to_genefile(input2,dict_max_tag,sys.stdout)
    input2.close()



