'''
This is the module you'll submit to the autograder.

There are several function definitions, here, that raise RuntimeErrors.  You should replace
each "raise RuntimeError" line with a line that performs the function specified in the
function's docstring.

For implementation of this MP, You may use numpy (though it's not needed). You may not 
use other non-standard modules (including nltk). Some modules that might be helpful are 
already imported for you.
'''

import math
from collections import defaultdict, Counter
from math import log
import numpy as np

# define your epsilon for laplace smoothing here
smoothness = 1e-5

def baseline(test, train):
    '''
    Implementation for the baseline tagger.
    input:  test data (list of sentences, no tags on the words, use utils.strip_tags to remove tags from data)
            training data (list of sentences, with tags on the words)
    output: list of sentences, each sentence is a list of (word,tag) pairs.
            E.g., [[(word1, tag1), (word2, tag2)], [(word3, tag3), (word4, tag4)]]
    '''
    #for each word w, count how many times w occurs with each tag
    test_tagged = []
    word_tag = defaultdict(lambda: defaultdict(int)) # [word][tag] init 0
    tag_count = defaultdict(int) # track most appeared tag

    for sentence in train:
        for word, tag in sentence:
            word_tag[word][tag] += 1
            tag_count[tag] += 1
    
    most_tag = max(tag_count, key=tag_count.get)

    
    for sentence in test:
        sentence_q = []
        for word in sentence:
            if word not in word_tag:
                sentence_q.append((word, most_tag))
            else:
                sentence_q.append((word, max(word_tag[word], key=word_tag[word].get)))
        test_tagged.append(sentence_q)    
    return test_tagged


def viterbi(test, train):
	'''
	Implementation for the viterbi tagger.
	input:  test data (list of sentences, no tags on the words)
		training data (list of sentences, with tags on the words)
	output: list of sentences with tags on the words
		E.g., [[(word1, tag1), (word2, tag2)], [(word3, tag3), (word4, tag4)]]
	'''
	test_tagged = []
	word_tags = defaultdict(lambda: defaultdict(int)) # count occurences of tag/word pairs
	tag_pairs = defaultdict(lambda: defaultdict(int)) # count occurences of tag pairs
	tag_count = defaultdict(int) # count tag 
	#handled by START/tag pairs

	for sentence in train: # get data from training set
		prev = None
		for word, tag in sentence:
			tag_count[tag] += 1 # count tags

			if prev is not None:
				tag_pairs[prev][tag] += 1 # increment tag pairs

			word_tags[tag][word] += 1 #increment word tag pair
			prev = tag



	transition_probs = {}
	emission_probs = {}
	tag_init = tag_pairs["START"]

	# Laplace Smoothing

	# Initial Probability
	denom = sum(tag_init.values()) + smoothness * (len(tag_init)+1)
	initial_prob = {tag: freq / denom for tag, freq in tag_init.items()}
	initial_prob["UNKNOWN"] = smoothness / denom

	# Transition Probability
	for prev, pairs in tag_pairs.items():
		transition_probs[prev] = {}
		for tag, freq in pairs.items():
			denom = sum(tag_pairs[prev].values()) + smoothness * (len(tag_pairs[prev])+1)
			transition_probs[prev][tag] = freq/denom
		transition_probs[prev]["UNKNOWN"] = smoothness/denom
	del transition_probs["START"]

	# Emission Probability
	for prev, pairs in word_tags.items():
		emission_probs[prev] = {}
		for tag, freq in pairs.items():
			denom = sum(word_tags[prev].values()) + smoothness*(len(word_tags[prev])+1)
			emission_probs[prev][tag] = freq/denom
	del emission_probs["START"]
	del emission_probs["END"]
	for tag_dict in emission_probs.values():
		tag_dict["UNKNOWN"] = smoothness/denom
		
	#log all values
	initial_p = {tag: math.log(item) for tag, item in initial_prob.items()}
	transition_p = {prev: {tag: math.log(item) for tag, item in pairs.items()} for prev, pairs in transition_probs.items()}
	emission_p = {tag: {word: math.log(item) for word, item in words.items()} for tag, words in emission_probs.items()}

	#construct the Trellis (Viterbi Algorithm)
	states = emission_p.keys()
    
	for sentence in test:
		viterbi_t = [{}]
		backpointer = [{}]

		for state in states:
			# Initialization
			viterbi_t[0][state] = initial_p.get(state, initial_p["UNKNOWN"]) + emission_p[state].get(sentence[0], emission_p[state]["UNKNOWN"])
			backpointer[0][state] = None

		for t in range(1, len(sentence)):
			viterbi_t.append({})
			backpointer.append({})
			for state in states:
				(max_prob, backpoint) = max((viterbi_t[t-1][prev_state] + transition_p[prev_state].get(state, transition_p[prev_state]["UNKNOWN"])
											, prev_state) for prev_state in states)
				viterbi_t[t][state] = max_prob + emission_p[state].get(sentence[t], emission_p[state]["UNKNOWN"])
				backpointer[t][state] = backpoint

		# find which state is the most probable state to end in
		best_path_prob = max(viterbi_t[-1].values())
		best_path_pointer = max(viterbi_t[-1], key=lambda k: viterbi_t[-1][k]) #termination step
		best_path = [best_path_pointer]
		for i in range(len(sentence)-1, 0, -1):
			best_path.insert(0, backpointer[i][best_path[0]])

		# Link tags with words
		sentence_list = []
		for i in range(0, len(sentence)):
			if i == len(sentence) -1:
				sentence_list.append((sentence[i], "END"))
			else:
				sentence_list.append((sentence[i], best_path[i]))
		test_tagged.append(sentence_list)

	return test_tagged 


def viterbi_ec(test, train):
    '''
    Implementation for the improved viterbi tagger.
    input:  test data (list of sentences, no tags on the words). E.g.,  [[word1, word2], [word3, word4]]
            training data (list of sentences, with tags on the words). E.g.,  [[(word1, tag1), (word2, tag2)], [(word3, tag3), (word4, tag4)]]
    output: list of sentences, each sentence is a list of (word,tag) pairs.
            E.g., [[(word1, tag1), (word2, tag2)], [(word3, tag3), (word4, tag4)]]
    '''
    raise NotImplementedError("You need to write this part!")



