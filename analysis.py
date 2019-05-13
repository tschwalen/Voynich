import parse
from collections import Counter

 
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



def char_positional_analysis(wf, cf):

	# initialize vectors for each character
	vectors = {c : [0] * 8 for c in cf}

	for word in wf:

		# get the range object that tells us 
		# how to index into the psositional 
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

		vectors[char_key] = map(lambda x : x / counts , un_norm_vec)

	return vectors




			










def preliminary_analysis(voynich):


	# subsection_analysis(voynich)
	
	# wf = word_frequencies(voynich[1])


	""" Finding the lonest valid word """
	# for word in list(wf):
	# 	if wf[word] < 3:
	# 		del wf[word]
	
	# character_frequencies(voynich[1])
	# longest = max(list(wf), key=len )
	# print(longest)
	# print(wf["qokeeodaiin"])














if __name__ == "__main__":
	voynich = parse.read_in_source(source)
	preliminary_analysis(voynich)
	