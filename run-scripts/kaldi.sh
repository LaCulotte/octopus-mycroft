# In kaldi folder

./src/online2bin/online2-tcp-nnet3-decode-faster --samp-freq=8000 --frames-per-chunk=20 --extra-left-context-initial=0 --frame-subsampling-factor=3 --min-active=200 --config=vosk-model-fr-0.6-linto/conf/online_nnet2_decoding.conf --max-active=7000 --beam=15.0 --lattice-beam=6.0 --acoustic-scale=1.0 --port-num=5050 --verbose=1 --read-timeout=1 vosk-model-fr-0.6-linto/am/final.mdl vosk-model-fr-0.6-linto/graph/HCLG.fst vosk-model-fr-0.6-linto/graph/words.txt

# Model references
# A model from [LINTO project](https://doc.linto.ai/#/services/linstt) with VOSK LM

# Licensed under AGPL

# WER on common voice and our test set

# %WER 16.25 [ 1552 / 9550, 200 ins, 235 del, 1117 sub ] exp/chain/tdnn/decode_test_cv_small_rescore/wer_11_1.0
# %WER 24.36 [ 18064 / 74145, 3309 ins, 5132 del, 9623 sub ] exp/chain/tdnn/decode_test_reseg_rescore/wer_11_0.0

# In folder :
# kaldi/vosk-model-fr-0.6-linto