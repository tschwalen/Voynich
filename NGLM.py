import math
from collections import Counter

start_token = "<s>"


class NG_Model:


	"""
	n : the 'n' of the n-gram
	k : degree of laplace smoothing
	"""
	def __init__(self, n, k):
		assert(n != 1)


		self.n = n
		self.k = k
		
		self.vocab = set()

		self.ngram_cnts = Counter()
		self.n_minusone_cnts = Counter()


	def get_vocab(self):
		return vocab

	def update(self, text):
		if not isinstance(text, list):
			text = text.split()
		
		# now text must be a list of strings
		n_grams = get_ngrams(self.n, text)

		n_minusone_grams = get_ngrams(self.n - 1, text, self.n - 1)

		#print(n_grams)
		#print(n_minusone_grams)


		self.ngram_cnts.update(n_grams)
		self.n_minusone_cnts.update(n_minusone_grams)


	# aka P(W | C)
	def prob(self, context, word, do_log=False):
		

		if isinstance(context, str):
			context = context.split()

		if len(context) < self.n - 1:
			padding = ["<s>"] * ((self.n - 1) - len(context))
			context = padding + context

		# add code to handle different types of input
		ngram_context = tuple(context[-(self.n - 1):])
		ngram = ngram_context + (word,)

		#print(ngram_context)
		#print(ngram)

		# no smoothing yet
		prob = self.ngram_cnts[ngram] / self.n_minusone_cnts[ngram_context] 

		if do_log:
			prob = math.log10(prob)
		return prob



	
	def random_word(self, context):
		''' Returns a random character based on the given context and the 
			n-grams learned by this model '''
		
		# we want context to be a list of strings
		if isinstance(context, str):
			context = context.split()

		if len(context) < self.n - 1:
			padding = ["<s>"] * ((self.n - 1) - len(context))
			context = padding + context
 
		context = tuple(context[-(self.n - 1):])

		max_prob = float("-inf")
		most_likely_word = None


		for ngram in self.ngram_cnts:
			if ngram[0: self.n - 1] == context:

				p = self.prob(context, ngram[-1], do_log=True)

				if p > max_prob:
					max_prob = p
					most_likely_word = ngram[-1]
		return most_likely_word


	def random_text(self, length):
		''' Returns text of the specified character length based on the
			n-grams learned by this model '''

		context = []



		pass

	def perplexity(self, text):
		''' Returns the perplexity of text based on the n-grams learned by
			this model '''
		pass





def get_ngrams(n, text, custom_padding=None):

	if not isinstance(text, list):
		word_tokens = text.split()
	else:
		word_tokens = text

	
	if custom_padding:
		padding = [start_token] * custom_padding
	else:
		padding = [start_token] * (n - 1)

	word_tokens = padding + word_tokens

	##print(word_tokens)

	n_grams = []
	for index in range(0, len(word_tokens) - n + 1):

		#context = word_tokens[index : index + n - 1]
		#word = word_tokens[index + n - 1]

		n_grams.append( tuple(word_tokens[index:index + n]) )

	return n_grams





if __name__ == "__main__":
	lm = NG_Model(2, 0)
	lm.update("I am Sam")
	lm.update("Sam I am")
	lm.update("I do not like green eggs and ham")

	print(lm.prob("<s>", "I"))
	print(lm.prob("<s>", "Sam"))
	print(lm.prob("am", "Sam"))
	print(lm.prob("I", "am"))
	print(lm.prob("I", "do"))
	##print(n_grams(3, "I have no shoes"))

