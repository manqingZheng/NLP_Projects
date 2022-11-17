import re
import sys
from collections import defaultdict
import math


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
                output_file.write("%s %s\n" % (line, dict_max_tag['_RARE_']))
        else:
            output_file.write("\n")


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




# import sys
# from collections import defaultdict
# import math


# def read_counts(counts_file, word_tag, word_dict, uni_tag):
#     for l in counts_file:
#         line = l.strip().split(' ')
#         if line[1] == 'WORDTAG':
#             word_tag[(line[3], line[2])] = int(line[0])
#             word_dict.append(line[3])
#         elif line[1] == '1-GRAM':
#             uni_tag[(line[2])] = int(line[0])

# def word_with_max_tagger(word_tag, word_dict, uni_tag, word_tag_max):
#     for word in word_dict:
#         max_tag = ''
#         max_val = 0.0
#         for tag in uni_tag:
#             if float(word_tag[(word, tag)]) / float(uni_tag[(tag)]) > max_val:
#                 max_val = float(word_tag[(word, tag)]) / float(uni_tag[(tag)])
#                 max_tag = tag
#         word_tag_max[(word)] = max_tag

# def tag_gene(word_tag_max, out_f, dev_file):
#     for l in dev_file:
#         line = l.strip()
#         if line:
#             if line in word_tag_max:
#                 out_f.write("%s %s\n" % (line, word_tag_max[(line)]))
#             else:
#                 out_f.write("%s %s\n" % (line, word_tag_max[('_RARE_')]))
#         else:
#             out_f.write("\n")

# def usage():
#     print ("""
#     python baseline.py [input_train_counts] [input_dev_file] > [output_file]
#         Read in counts file and dev file, produce tagging results.
#     """)


# if __name__ == "__main__":

#     if len(sys.argv)!=3: # Expect exactly one argument: the training data file
#         usage()
#         sys.exit(2)

#     try:
#         counts_file = open(sys.argv[1], "r")
#         dev_file = open(sys.argv[2], 'r')
#     except IOError:
#         sys.stderr.write("ERROR: Cannot read inputfile %s.\n" % arg)
#         sys.exit(1)
        
#     word_tag, uni_tag, word_tag_max = defaultdict(int), defaultdict(int), defaultdict(int)
#     word_dict = []

#     read_counts(counts_file, word_tag, word_dict, uni_tag)
#     counts_file.close()
#     word_with_max_tagger(word_tag, word_dict, uni_tag, word_tag_max)
#     tag_gene(word_tag_max, sys.stdout, dev_file)
#     dev_file.close()
