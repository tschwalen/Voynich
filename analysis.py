import parse
from collections import Counter
import numpy as np
import functools as ft
import operator as op
import math
from NGLM import NG_Model

np.set_printoptions(precision=5)

 
source="data/ivtt/ZL_ivtff_1b.txt"

i_codes = { "A" :   "Astronomical (excluding zodiac)",
	"B"  :  "Biological",
	"C"   : "Cosmological",
	"H"   : "Herbal",
	"P"   : "Pharmaceutical",
	"S"   : "Marginal stars only",
	"T"   : "Text‐only page (no illustrations)",
	"Z"   : "Zodiac"}


def word_frequencies(pages, top=15, do_print=True):
	list_of_pages = pages

	# base word frequencies
	word_counts = Counter()
	for page in list_of_pages:
		#print(page.name)
		for line in page.lines:
			#print(line.line_num)
			word_counts.update(line.get_words_simple())

	

	if do_print:
		frequencies = word_counts.most_common(top)
		for x in frequencies:
			print("{word}  :  {freq}".format(word=x[0], freq=x[1]))

	return word_counts

def character_frequencies(pages, top=15, do_print=True):
	list_of_pages = pages

	# base word frequencies
	char_counts = Counter()
	for page in list_of_pages:

		for line in page.lines:
			for word in line.get_words_simple():
				char_counts.update(word)
			
	
	if do_print:
		frequencies = char_counts.most_common(top)
		for x in frequencies:
			print("{char}  :  {freq}".format(char=x[0], freq=x[1]))

	return char_counts

def subsection_frequencies(voynich, do_print=False, include_T=False):
	global i_codes

	"""
	In the trasciption file, each page is marked by what sort of illustration appears. The codes are as follows:
	A    Astronomical (excluding zodiac)
	B    Biological
	C    Cosmological
	H    Herbal
	P    Pharmaceutical
	S    Marginal stars only
	T    Text‐only page (no illustrations)
	Z    Zodiac
	
	(I'm going to ignore "Text Only because the illustrations is what I'm most interested in here")

	The labels might be a little arbitrary (I haven't seen all of the MS illustrations) but in any case, separating 
	them now allows me to do both fine grained and coarse grained (combining categories like Astronomy and Cosmology)
	analysis should I choose to do so.

	"""

	list_of_pages = voynich[1]

	subsection_pages = {"A" : [], "B": [], "C": [], "H": [], "P": [], "S": [], "Z": [] }

	if include_T:
		subsection_pages["T"] = []

	for page in list_of_pages:

		# value of the $I= for the page variables
		illustration_type = page.vars["I"]
		
		#skipping text-only for now
		if illustration_type != "T":
			subsection_pages[illustration_type].append(page)

	subsection_frequency_data = {}

	for i_type in subsection_pages:
		pages = subsection_pages[i_type]
		if do_print:
			print("Currently Processing {i}".format(i=i_codes[i_type]))

		word_f = word_frequencies(pages, 10, do_print)
		char_f = character_frequencies(pages, 10, do_print)

		subsection_frequency_data[i_type] = (word_f, char_f) 

	return subsection_frequency_data

# perform a set subtract on counters since apparantly standard python doesn't have this
def counter_set_sub(lcounter, rcounter):
	result_counter = lcounter.copy()

	for word in rcounter:
		del result_counter[word]
	return result_counter

"""
For each illustration type (I'm calling them subsections for some reason) find out what words appear in it,
but not some other illustration type
"""
def simple_subsection_differences(freq_data, top=5, do_print=False):
	for cat in freq_data:
		for other_cat in freq_data:
			if cat != other_cat:
				print("Top {top} words that appear in {cat}, but not in {other_cat}".format(top=top, cat=i_codes[cat], other_cat=i_codes[other_cat]))
				
				# ~~~~~~~~~~~~
				words = counter_set_sub(freq_data[cat][0], freq_data[other_cat][0]) 
				for tup in words.most_common(top):
					print("{word}  :  {freq}".format(word=tup[0], freq=tup[1]))

"""
Report which words ONLY appear in one subsection/illustration type
"""
def absolute_subsection_differences(freq_data, top=10, do_print=False):
	for cat in freq_data:

		words = freq_data[cat][0]
		for other_cat in freq_data:
			if cat != other_cat:
				
				# ~~~~~~~~~~~~
				words = counter_set_sub(words, freq_data[other_cat][0]) 


		print("Top {top} words that appear only in {cat}".format(top=top, cat=i_codes[cat]))
		for tup in words.most_common(top):
			print("{word}  :  {freq}".format(word=tup[0], freq=tup[1]))




def subsection_analysis(voynich, top=5, do_print=False):
	global i_codes

	freq_data = subsection_frequencies(voynich, include_T=True)

	#simple_subsection_differences(freq_data, top, do_print)
	absolute_subsection_differences(freq_data, 10, do_print)
	

######################################################################################################

"""

0  1  2  3 -3 -2 -1
b  a  l  l  a  s  t  -> (-3, 4)

0  1  2 -3 -2 -1
b  r  i  d  g  e  -> (-3, 3)

0  1  2 -2 -1
s  t  i  c  k  ->  range(-2, 3)

0  1 -2 -1
b  a  l  l     ->  range(-2, 2)

0  1 -1
h  e  y		   ->  range(-1, 2)

0 -1
n  o           ->  range(-1, 1)

0
a              ->  range(0, 1)
"""
def range_calc(x):
	"""
	basically this ensures we don't get
	overlapping scores when calculating
	the positional frequency of characters
	since for strings shorter than len 8
	there is overlap for range (-4, 4)
	eg, "hey"[-1] == "hey"[2]
	
	(not to mention out of range errors)
	"""
	if x > 8:
		x = 8

	lo = 0 - x // 2
	hi = lo + x
	return range(lo, hi)



def calculate_char_pos_vectors(wf, cf, digs=3, do_round=True):

	# initialize vectors for each character
	vectors = {c : [0] * 8 for c in cf}

	for word in wf:

		# get the range object that tells us 
		# how to index into the positional 
		# vector
		v_range = range_calc(len(word))

		word_index = 0
		for vi in v_range:
			"""
			we iterate over the word's characters
			in the order that corrosponds to it's 
			index in the positional frequency 
			vector.
			"""
			char = word[vi]

			"""
			since we have the frequency of the word, we
			can update the count in the posfreq vector
			like this, since if char c occurs at position
			x in word w, and word w occurs z times in the
			MS, then we know that char c occurs at position
			x at least z times
			"""
			vectors[char][vi] += wf[word]

	# now normalize each vector by the character's count in the ms
	for char_key in vectors:
		counts = cf[char_key]

		un_norm_vec = vectors[char_key]

		for i in range(0, len(un_norm_vec)):

			# might not want to round when doing calculations, but maybe for presentation
			if do_round:
				vectors[char_key][i] = round( vectors[char_key][i] / counts, digs)
			else:
				vectors[char_key][i] = vectors[char_key][i] / counts

	return vectors


def fav_pos_top_20(wf, cf):
	top20 = {}
	for char, freq in cf.most_common(20):
		top20[char] = pos_freq_vecs[char]

	top20_most_freq_pos = [""] * 8
	for i in range(0, len(top20_most_freq_pos)):

		col = { k : top20[k][i] for k in top20 }

		top20_most_freq_pos[i] = max(col, key=col.get)

	print(top20_most_freq_pos)

def char_pos_overall_weights(wf, cf):
	chars = sorted(list(pos_freq_vecs))

	
	for char, freq in cf.most_common():
		print("{ch} : {vec}      ->   {freq}".format(ch=char, vec=pos_freq_vecs[char], freq=freq))



def start_score(pw_vector):
	"""
	Calculate the start score of a positional weight vector
	"""

	# subtract end likelyhood from start likelyhood
	return ft.reduce(op.add, pw_vector[0:4], 0) - ft.reduce(op.add, pw_vector[4:8], 0)

def end_score(pw_vector):
	"""
	Calculate the start score of a positional weight vector
	"""

	# subtract end likelyhood from start likelyhood
	return ft.reduce(op.add, pw_vector[4:8], 0) - ft.reduce(op.add, pw_vector[0:4], 0)

def weighted_start_score(pw_vector, freq):
	return start_score(pw_vector) * math.log10(freq)

def weighted_end_score(pw_vector, freq):
	return end_score(pw_vector) * math.log10(freq)


def start_end_score_analysis(wf, cf):
	""" we're going to exclude single character words and very infrequent words """

	
	for word in list(wf):
		if len(word) < 2:
			del wf[word]

		# with the weighted scores, infrequent
		
		if wf[word] < 2:
			del wf[word]
		


	pos_freq_vecs = calculate_char_pos_vectors(wf, cf)

	chars = sorted(list(pos_freq_vecs))

	""" Calculate start and end scores for all characters """
	start_scores = {ch : weighted_start_score(pos_freq_vecs[ch], cf[ch]) for ch in chars}
	end_scores = {ch : weighted_end_score(pos_freq_vecs[ch], cf[ch]) for ch in chars}
	"""
	sorted_ss = [(k, start_scores[k]) for k in sorted(start_scores, key=start_scores.get, reverse=True)]
	sorted_es = [(k, end_scores[k]) for k in sorted(end_scores, key=end_scores.get, reverse=True)]
	"""

	sorted_ss = [(k, start_scores[k]) for k in sorted(start_scores, key=start_scores.get, reverse=True)]
	sorted_es = [(k, end_scores[k]) for k in sorted(end_scores, key=end_scores.get, reverse=True)]

	"""
	print("Start Scores:")
	for ch, sc in sorted_ss:
		print("{ch} : {sc} : (occurs {f} times)".format(ch=ch, sc=sc, f=cf[ch]))


	print("\nEnd Scores:")
	for ch, sc in sorted_es:
		print("{ch} : {sc} : (occurs {f} times)".format(ch=ch, sc=sc, f=cf[ch]))
	"""
	print("Weighted Start Scores:")
	for ch, sc in sorted_ss:
		print("{ch} : {sc} : (occurs {f} times)".format(ch=ch, sc=sc, f=cf[ch]))


	print("\nWeighted End Scores:")
	for ch, sc in sorted_es:
		print("{ch} : {sc} : (occurs {f} times)".format(ch=ch, sc=sc, f=cf[ch]))


def char_positional_analysis(wf, cf):

	
	start_end_score_analysis(wf, cf)
	"""
	pos_freq_vecs = calculate_char_pos_vectors(wf, cf)

	chars = sorted(list(pos_freq_vecs))

	
	for char, freq in cf.most_common():
		print("{ch} : {vec}      ->   {freq}".format(ch=char, vec=pos_freq_vecs[char], freq=freq))
	"""

######################################################################################################
	



def other_text_lm():
	lines = 5198

	start_line = 90

	source = "data/evagatorium.txt"

	lines = []

	line_num = 0
	with open(source, "r") as ins:
			
			for line in ins:

				if line_num < start_line:
					line_num += 1
					continue

				if line_num > lines:
					break


				
				array.append(line)



def language_model_analysis(voynich):

	list_of_pages = voynich[1]

	training_set = []

	test_set = []

	lm = NG_Model(3, 3)

	# let the test set be every x line, and the training set be the remainder

	num = 0
	for page in list_of_pages:
		#print(page.name)
		for line in page.lines:

			if num % 2 == 0:
				test_set.append(line.get_words_simple())
			else:
				training_set.append(line.get_words_simple())

			num += 1

	print(num)

	# now train the lm
	for line in training_set:
		lm.update(line)

	print(len(lm.vocab))

	# calculate the perplexity
	perplexity = lm.corpus_perplexity(test_set)

	#generate some random text
	sample_line = lm.random_text(8)

	print("perplexity: {p}".format(p=perplexity))
	print("Sample Sentence: {s}.".format(s=sample_line))




def preliminary_analysis(voynich):


	# subsection_analysis(voynich)
	
	#wf = word_frequencies(voynich[1], do_print=False)
	#cf = character_frequencies(voynich[1], do_print=False)

	""" Finding the lonest valid word """
	# for word in list(wf):
	# 	if wf[word] < 3:
	# 		del wf[word]
	
	# character_frequencies(voynich[1])
	# longest = max(list(wf), key=len )
	# print(longest)
	# print(wf["qokeeodaiin"])

	# ~~~~ char positional analysis
	#char_positional_analysis(wf, cf)
	language_model_analysis(voynich)








if __name__ == "__main__":
	voynich = parse.read_in_source(source)
	preliminary_analysis(voynich)
	