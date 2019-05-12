import parse
from collections import Counter

 
source="data/ivtt/ZL_ivtff_1b.txt"


def word_frequencies(voynich, top=15):
	list_of_pages = voynich[1]

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

def character_frequencies(voynich, top=15):
	list_of_pages = voynich[1]

	# base word frequencies
	char_counts = Counter()
	for page in list_of_pages:

		for line in page.lines:
			for word in line.get_words_simple():
				char_counts.update(word)
			
	frequencies = char_counts.most_common(top)

	for x in frequencies:
		print("{char}  :  {freq}".format(char=x[0], freq=x[1]))

def preliminary_analysis(voynich):
	
	#word_frequencies(voynich)
	character_frequencies(voynich)














if __name__ == "__main__":
	voynich = parse.read_in_source(source)
	preliminary_analysis(voynich)
	