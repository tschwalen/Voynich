import re
import pprint as pp


source = "data/ivtt/ZL_ivtff_1b.txt"

class VoynichLine:

	def __init__(self, locus, text):
		self.pg_name = locus[0]
		self.line_num = locus[1]
		self.code = locus[2]

		self.text = text


	# returns the simplest string representation of this line
	# uncertain characters get their first choice
	# ligatures are treated as two separate characters
	def get_words_simple(self, confident_spaces=True):
		if confident_spaces:
			split_re = r"\.|,"
		else:
			split_re = r"\."

		line = self.text

		# go ahead an yeet every inline comment
		line = re.sub(r"<.*>", "", line)

		# we're treating ligatures as sequences of characters
		line = line.replace("{", "").replace("}", "")

		# now we reslove conflicting characters to the first choice
		line = simple_bracket_extract(line)

		line = weirdo_to_unicde(line)

		""" 
		NOTE:
		For now I am leaving in the ?, ???, and * characters for
		different types of unreadable characters even though they
		don't provide any important information for analysis.
		They'll be easy to remove should I decide to do so.
		"""


		# let's tokenize the line
		line = re.split(split_re, line)


		#now we can remove any commas if they still exist
		line = map(lambda x : x.replace(",", "") , line)

		# now we should have a list of strings that cleanly
		# represents this line of the MS
		return line

	def get_string_simple(self, confident_spaces=True):
		return " ".join(map(str, self.get_words_simple(confident_spaces)))


# in cases where the transcriber was unsure of the character
# they just wrote [a:b] where the first character is the 
# most likely one. Given a string, this method detects these 
# instances and returns a strong where only the first character
# or characters are present (in about the most un-pythonic way
# possible)
def simple_bracket_extract(line):
	output_line = ""
	i = 0
	while i < len(line):
		c = line[i]

		if c == "[":
			i += 1
			c = line[i]

			while c != ":":
				output_line += c
				i += 1
				c = line[i]

			while c != "]":
				i += 1
				c = line[i]
		else:
		    output_line += c  
		
		i += 1

	return output_line

# "weirdos" i.e. characters that are infrequent but definite
# are given a high printable ascii value, but are encoded as 
# "@123;" where the thee digit number is the ascii code of the
# character. Since python can handle wierd characters, I'm just
# going to insert them into the string
def weirdo_to_unicde(line):
	output_line = ""
	i = 0
	while i < len(line):
		c = line[i]

		if c == "@":
			i += 1

			num = line[i:i+3]
			output_line += chr(int(num))

			i += 3

		else:
			output_line += c
		i += 1

	return output_line

def test_voynich_line():
	examples = set()
	examples.add("??doin.chol.dain.cthal.dar.shear.kaiin.dar.shey.cthar")	
	examples.add("dchar.shcthaiin.okaiir.chey.@192;chy.@130;tol.cthols.dlo{ct}o")
	examples.add("ycho.tchey.chekain.sheo,pshol.dydyd.cthy.dai[{cto}:@194;]y")
	examples.add("shor.ckhy.daiiny.<->chol,dan<$>")
	examples.add("otosey.<!star><->sary")

	dummy_locus = ("test", "test", "test")

	for ex in examples:
		page = VoynichLine(dummy_locus, ex)
		print(ex)

		line = page.get_string_simple()

		print(line)
		print("")




class VoynichPage:


	def __init__(self, pg_name, pg_vars):
		self.name = pg_name
		self.vars = pg_vars

		self.lines = []


	def add_line(self, locus, text):
		self.lines.append(VoynichLine(locus, text))

	def __str__(self):
		return "<{n}>".format(n=self.name)

	def __repr__(self):
		return self.__str__()

def read_in_source(source):
 
	pg_header_re = r"(<f[0-9]+[rv][0-9]?>)\s+(<!.*>)"
	locus_re = r"<(f[0-9]+[rv][0-9]?)\.([0-9]+),(...)>"

	result = None

	with open(source, "r") as f:
		
		pages = []

		# read the header to know what format we're using
		header = f.readline().split()
		alphabet = header[1]

		current_page = None


		# begin reading the rest of the file
		line = f.readline().rstrip("\r\n")

		while line:
			#print(line)
			# ivtff has '#' line comments just like python
			if line[0] != "#":

				# check if line is a page header, and read it if so
				match = re.match(pg_header_re, line)
				if match:
					# print(line)
					# print(match.groups())
					pg_name = match.groups()[0][1:-1]
					pg_vars = read_pg_vars(match.groups()[1])
					#print(line)
					
					#print(pg_name)

					new_page = VoynichPage(pg_name, pg_vars)

					if current_page != None:
						pages.append(new_page)
					current_page = new_page

				elif re.match(locus_re, line):
					# if it's not a comment or page header, then it must be a regular line

					# first get the locus
					locus = re.match(locus_re, line).groups()
					
					text = line.split()[1]
					current_page.add_line(locus, text)

				else:
					pass
					
			# increment page
			line = f.readline().rstrip("\r\n")
		result = (alphabet, pages)

		#pp.pprint(pages)

	return result


def read_pg_vars(vars_string):
	# strip angle brackets and split into individual var assignments
	pg_vars = vars_string[2 : -1].split()

	pg_var_values = {}

	# all variable names and values are 1 character and
	# are in the format: $V=X
	for stmt in pg_vars:
		pg_var_values[stmt[1]] = stmt[3]

	return pg_var_values



					





if __name__ == "__main__":
	read_in_source(source)
