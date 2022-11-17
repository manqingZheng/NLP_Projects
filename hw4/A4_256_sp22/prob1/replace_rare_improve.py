import re
import sys
from collections import defaultdict
import math
from string import punctuation

def get_count(corpus_file):
    """
    Get an iterator object over the corpus file. The elements of the
    iterator contain (word, ne_tag) tuples. Blank lines, indicating
    sentence boundaries return (None, None).
    """
    count_word = defaultdict(int)
    for l in corpus_file:
        line = l.strip()
        if line: # Nonempty line
            # Extract information from line.
            # Each line has the format
            # word pos_tag phrase_tag ne_tag
            fields = line.split(" ")
            word = fields[0]
            #phrase_tag = fields[-2] #Unused
            #pos_tag = fields[-3] #Unused
            count_word[word] += 1
    return count_word

def rare_classifier(word):
    if word.isdigit():
        return "_NUMBER_"
    if any((w in punctuation) for w in word):
        return "_PUNCTUATION_"
    if word.isupper():
        return "_CAPITAL_"
    if len(word)>10:
        return"_LongWord_"
    # if (',' in word or '.' in word):
    #     return "_HasDot_"
    return "_RARE_"



def replace_with_rare(corpus_file, count_word, output_file):
    # rare_words = open('rare_words.txt', 'w')
    for l in corpus_file:
        line = l.strip()
        if line:
            fields = line.split(" ")
            tag = fields[1]
            word = fields[0]
            if count_word[word] < 5:
                rare_word = rare_classifier(word)
                output_file.write(rare_word  + " %s\n" % tag)
            else:
                output_file.write(line + '\n')
        else:
            output_file.write('\n')




if __name__ == "__main__":

    if len(sys.argv)!=2:  # Expect exactly one argument: the training data file
        sys.exit(2)

    try:
        input = open(sys.argv[1],"r")
    except IOError:
        sys.stderr.write("ERROR: Cannot read inputfile %s.\n" % arg)
        sys.exit(1)

    count_word = get_count(input)
    input.close()

    try:
        input = open(sys.argv[1], "r")
    except IOError:
        sys.stderr.write("ERROR: Cannot read inputfile %s.\n" % arg)
        sys.exit(1)

    replace_with_rare(input, count_word, sys.stdout)
    input.close()



