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
		
		# keep V updated
		for word in text:
			self.vocab.add(word)

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
			padding = [start_token] * ((self.n - 1) - len(context))
			context = padding + context

		# add code to handle different types of input
		ngram_context = tuple(context[-(self.n - 1):])
		ngram = ngram_context + (word,)

		#print(ngram_context)
		#print(ngram)

		# simple k smoothing right now
		prob = ( self.ngram_cnts[ngram] + self.k ) / (self.n_minusone_cnts[ngram_context] + (self.k * len(self.vocab))) 

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
			padding = [start_token] * ((self.n - 1) - len(context))
			context = padding + context
 
		context = tuple(context[-(self.n - 1):])

		max_prob = float("-inf")
		most_likely_word = None


		for word in self.vocab:


			p = self.prob(context, word, do_log=True)
			if p > max_prob:
				max_prob = p
				most_likely_word = word
				
		return most_likely_word


	def random_text(self, length):
		''' Returns text of the specified character length based on the
			n-grams learned by this model '''

		context = []
		phrase = ""

		for i in range(0, length):
			next_word = self.random_word(context)
			context.append(next_word)
			phrase += next_word
			phrase += " "

		return phrase


	def perplexity(self, text):
		''' Returns the perplexity of text based on the n-grams learned by
			this model '''
		pass


	def entropy(self, text):
		"""
		# Adapted From NLTK's entropy

		Calculate the approximate cross-entropy of the n-gram model for a
		given evaluation text.
		This is the average log probability of each word in the text.

		:param text: words to use for evaluation
		:type text: list(str)
		"""

		if not isinstance(text, list):
			text = text.split()

		padding = [start_token] * (self.n - 1)


		e = 0.0
		text = padding + text
		for index in range(0, len(text) - self.n + 1):
			context = tuple(text[index : index + self.n - 1])
			word = text[index + self.n - 1]
			e += -(self.prob(context, word, do_log=True))

		return e / float(len(text) - (self.n - 1))

	def perplexity(self, text):
		"""
	
		# Adapted From NLTK's entropy

		Calculates the perplexity of the given text.
		This is simply 2 ** cross-entropy for the text.

		:param text: words to calculate perplexity of
		:type text: list(str)
		"""

		return math.pow(2.0, self.entropy(text))




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
	lm = NG_Model(3, 0.1)
	lm.update("I am Sam")
	lm.update("Sam I am")
	lm.update("I do not like green eggs and ham")

	print(lm.prob("<s>", "I"))
	print(lm.prob("<s>", "Sam"))
	print(lm.prob("am", "Sam"))
	print(lm.prob("I", "am"))
	print(lm.prob("I", "do"))
	print(lm.random_text(7))
	print(lm.perplexity("I do not like green eggs and ham"))
	print(lm.perplexity("I do not like red beans and rice"))
	print(lm.perplexity("asdf wefwe eefer"))
	##print(n_grams(3, "I have no shoes"))

