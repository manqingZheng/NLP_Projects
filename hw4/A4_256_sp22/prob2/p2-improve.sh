python3 replace_rare_improve.py gene.train > gene.train_rare_improve 
python3 count_freqs.py gene.train_rare_improve  > gene.counts_rare_improve 
python3 viterbi_algo_improve.py gene.counts_rare_improve  gene.dev > gene_dev.p4.out
python3 eval_gene_tagger.py gene.key gene_dev.p4.out