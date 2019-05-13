
start_token = "<s>"



def n_grams(n, text):
	word_tokens = text.split()

	padding = [start_token] * n

	word_tokens = padding + word_tokens

	print(word_tokens)

	n_grams = []
	for index in range(0, len(word_tokens) - n):

		context = word_tokens[index : index + n]
		word = word_tokens[index + n]

		n_grams.append( (tuple(context), word) )

	return n_grams

if __name__ == "__main__":

	print(n_grams(3, "I have no shoes"))

