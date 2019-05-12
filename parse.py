import re


source = "data/ivtt/ZL_ivtff_1b.txt"

def read_in_source(source):


	pg_header_re = "<f[0-9]+[rv]>\\s+<!.*>"

	with open(source, "r") as f:
		
		pages = []

		# read the header to know what format we're using
		header = f.readline().split()
		alphabet_string = header[1]

		# print(header)
		# print(alphabet_string)

		# begin reading the rest of the file
		line = f.readline().rstrip("\r\n")

		while line:
			#print(line)
			# ivtff has '#' line comments just like python
			if line[0] != "#":

				# check if line is a page header, and read it if so
				if re.match(pg_header_re, line):
					print(line)



			line = f.readline().rstrip("\r\n")





					




if __name__ == "__main__":
	read_in_source(source)
