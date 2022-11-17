python3 replace_infrequent.py gene.train > gene.train_rare 
python3 count_freqs.py gene.train_rare > gene.counts_rare
python3 viterbi_algo.py gene.counts_rare gene.dev > gene_dev.p3.out
python3 eval_gene_tagger.py gene.key gene_dev.p3.out