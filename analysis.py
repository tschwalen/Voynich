import parse
from collections import Counter

 
source="data/ivtt/ZL_ivtff_1b.txt"


def word_frequencies(pages, top=15):
	list_of_pages = pages

	# base word frequencies
	word_counts = Counter()
	for page in list_of_pages:
		#print(page.name)
		for line in page.lines:
			#print(line.line_num)
			word_counts.update(line.get_words_simple())

	frequencies = word_counts.most_common(top)
	for x in frequencies:
		print("{word}  :  {freq}".format(word=x[0], freq=x[1]))

	return word_counts

def character_frequencies(pages, top=15):
	list_of_pages = pages

	# base word frequencies
	char_counts = Counter()
	for page in list_of_pages:

		for line in page.lines:
			for word in line.get_words_simple():
				char_counts.update(word)
			
	frequencies = char_counts.most_common(top)

	for x in frequencies:
		print("{char}  :  {freq}".format(char=x[0], freq=x[1]))

	return char_counts

def subsection_analysis(voynich):
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

	for page in list_of_pages:
		



def preliminary_analysis(voynich):



	
	#word_frequencies(voynich[1])
	#character_frequencies(voynich[1])














if __name__ == "__main__":
	voynich = parse.read_in_source(source)
	preliminary_analysis(voynich)
	