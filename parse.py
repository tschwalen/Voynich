import re
import pprint as pp


source = "data/ivtt/ZL_ivtff_1b.txt"


class VoynichPage:


	def __init__(self, pg_name, pg_vars):
		self.name = pg_name
		self.vars = pg_vars

		self.lines = []


	def __str__(self):
		return "<{n}>".format(n=self.name)

	def __repr__(self):
		return self.__str__()

def read_in_source(source):

	# < page . num , code ; T > 
	# <f112v.11,+P0>   
	pg_header_re = r"(<f[0-9]+[rv][0-9]?>)\s+(<!.*>)"
	locus_re = r"<(f[0-9]+[rv])\.([0-9]+),(...)>"

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
				else:
					pass
					# if it's not a comment or page header, then it must be a regular line

					# first get the locus
					#locus = re.match(locus_re, line).groups()




			# increment page
			line = f.readline().rstrip("\r\n")





		pp.pprint(pages)


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
