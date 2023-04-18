import sinol_make.config as config
import os, subprocess

def compile(program, compile_log = None):
	"""
	Compile a program
	"""
	ext = os.path.splitext(program)[1]

	if ext == '.cpp':
		compile_cpp(program, compile_log)
        

def compile_cpp(program, compile_log = None):
	"""
	Compile a C++ program
	"""

	config = config.Config()
	flags = '-O3 -lm -Werror -Wall -Wextra -Wshadow -Wconversion -Wno-unused-result -Wfloat-equal'

	if compile_log is None:
		stdout = subprocess.DEVNULL
		stderr = subprocess.DEVNULL
	else:
		stdout = compile_log
		stderr = subprocess.STDOUT
	
	subprocess.call([config.get('cpp_compiler'), program, '-o', program + '.e', flags], stdout=stdout, stderr=stderr)

    