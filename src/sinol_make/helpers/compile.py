import os
import subprocess
import sys
import sinol_make.helpers.compiler as compiler
from sinol_make.interfaces.Exceptions import CompilationException

def compile(program, output, compilers = None, compile_log = None):
	"""
	Compile a program
	compilers - A dictionary of compilers to use. If not set, the default compilers will be used
	"""
	ext = os.path.splitext(program)[1]
	arguments = []
	if ext == '.cpp':
		arguments = [compilers['cpp_compiler_path'] or compiler.get_cpp_compiler_path(),
	       			 program, '-o', output] + \
					 '-O3 -lm -Werror -Wall -Wextra -Wshadow -Wconversion -Wno-unused-result -Wfloat-equal'.split(' ')
	elif ext == '.c':
		arguments = [compilers['c_compiler_path'] or compiler.get_c_compiler_path(),
	       			 program, '-o', output] + \
					 '-O3 -lm -Werror -Wall -Wextra -Wshadow -Wconversion -Wno-unused-result -Wfloat-equal'.split(' ')
	elif ext == '.py':
		if sys.platform == 'win32' or sys.platform == 'cygwin':
			# TODO: Make this work on Windows
			pass
		else:
			open(output, 'w', encoding='utf-8').write('#!/usr/bin/python3\n')
			open(output, 'a', encoding='utf-8').write(open(program, 'r', encoding='utf-8').read())
			subprocess.call(['chmod', '+x', output])
		arguments = [compilers['python_interpreter_path'] or compiler.get_python_interpreter_path(),
	       			 '-m', 'py_compile', program]
	elif ext == '.java':
		raise NotImplementedError('Java compilation is not implemented')
	else:
		raise CompilationException('Unknown file extension: ' + ext)

	process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	process.wait()
	out, _ = process.communicate()
	if compile_log is not None:
		compile_log.write(out.decode('utf-8'))
		compile_log.close()
	else:
		print(out.decode('utf-8'))

	if process.returncode != 0:
		raise CompilationException('Compilation failed')
	else:
		return True
