import os.path
import re
from codecs import open

def parse_editorconfig(filename):
	if not os.path.isfile(filename):
		return

	# Regular expressions for parsing section header.
	SECTRE = re.compile(
		r"""

		\s *                                # Optional whitespace
		\[                                  # Opening square brace

		(?P<header>                         # One or more characters excluding
			( [^\#;] | \\\# | \\; ) +       # unescaped # and ; characters
		)

		\]                                  # Closing square brace

		""", re.VERBOSE
	)
	# Regular expression for parsing option name/values.
	OPTRE = re.compile(
		r"""

		\s *                                # Optional whitespace
		(?P<option>                         # One or more characters excluding
			[^:=\s]                         # : a = characters (and first
			[^:=] *                         # must not be whitespace)
		)
		\s *                                # Optional whitespace
		(?P<vi>
			[:=]                            # Single = or : character
		)
		\s *                                # Optional whitespace
		(?P<value>
			. *                             # One or more characters
		)
		$

		""", re.VERBOSE
	)

	in_section = False
	current_section = None
	config = {}

	with open(filename, encoding='utf-8') as fp:
		line = fp.readline()
		if line.startswith(unicode('\ufeff')):
				line = line[1:]  # Strip UTF-8 BOM
		
		while True:
			# a section header or option header?
			match_object = SECTRE.match(line)
			if match_object:
				section_name = match_object.group('header')
				config[section_name] = {}
				current_section = section_name
				in_section = True
				optname = None
			else:
				match_object = OPTRE.match(line)
				if match_object:
					optname, vi, optval = match_object.group('option', 'vi', 'value')
					if ';' in optval or '#' in optval:
						# ';' and '#' are comment delimiters only if
						# preceeded by a spacing character
						mo = re.search('(.*?) [;#]', optval)
						if mo:
							optval = mo.group(1)
					optval = optval.strip()
					# allow empty values
					if optval == '""':
						optval = ''
					optname = optname.rstrip().lower()
					if in_section:
						config[current_section][optname] = optval
				else:
					# unrecognized line type.
					pass
			line = fp.readline()
			if not line:
				break
			# comment or blank line?
			while line.strip() == '' or line[0] in '#;':
				line = fp.readline()

	return config