import sinol_make.helpers.compiler as compiler
from sinol_make.interfaces.Errors import CompilationError
import os, subprocess, sys

def compile(program, output, compile_log = None, args = None):
	"""
	Compile a program
	args - ArgParser arguments. Used to get compiler flags if set
	"""
	ext = os.path.splitext(program)[1]

	if ext == '.cpp':
		compile_cpp(program, output, compile_log, args)
	elif ext == '.c':
		compile_c(program, output, compile_log, args)
	elif ext == '.py':
		compile_python(program, output, compile_log, args)
	elif ext == '.java':
		compile_java(program, output, compile_log, args)
	else:
		raise CompilationError('Unknown file extension: ' + ext)


def compile_c(program, output, compile_log = None, args = None):
	"""
	Compile a C program
	compile_log - A file to write the compilation log to
	"""
	
	flags = '-O3 -lm -Werror -Wall -Wextra -Wshadow -Wconversion -Wno-unused-result -Wfloat-equal'.split(' ')
	
	process = subprocess.Popen([compiler.get_c_compiler(args), program, '-o', output] + flags, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	process.wait()
	out, _  = process.communicate()
	if compile_log is not None:
		compile_log.write(out.decode('utf-8'))
		compile_log.close()
	else:
		print(out.decode('utf-8'))
	
	if process.returncode != 0:
		raise CompilationError('Compilation failed')
	else:
		return True


def compile_cpp(program, output, compile_log = None, args = None):
	"""
	Compile a C++ program.
	compile_log - A file to write the compilation log to
	"""

	flags = '-O3 -lm -Werror -Wall -Wextra -Wshadow -Wconversion -Wno-unused-result -Wfloat-equal'.split(' ')
	
	process = subprocess.Popen([compiler.get_cpp_compiler(args), program, '-o', output] + flags, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	process.wait()
	out, _ = process.communicate()
	if compile_log is not None:
		compile_log.write(out.decode('utf-8'))
		compile_log.close()
	else:
		print(out.decode('utf-8'))
    
	if process.returncode != 0:
		raise CompilationError('Compilation failed')
	else:
		return True


def compile_python(program, output, compile_log = None, args = None):
	"""
	Compile a Python program
	compile_log - A file to write the compilation log to
	"""

	if sys.platform == 'win32':
		# TODO: Make this work on Windows
		pass
	else:
		open(output, 'w').write('#!/usr/bin/python3\n')
		open(output, 'a').write(open(program, 'r').read())
		subprocess.call(['chmod', '+x', output])
	
	process = subprocess.Popen([compiler.get_python_interpreter(args), '-m', 'compileall', output], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	process.wait()
	out, _ = process.communicate()
	if compile_log is not None:
		compile_log.write(out.decode('utf-8'))
		compile_log.close()
	else:
		print(out.decode('utf-8'))

	if process.returncode != 0:
		raise CompilationError('Compilation failed')
	else:
		return True
	
def compile_java(program, output, compile_log = None, args = None):
	"""
	Compile a Java program
	compile_log - A file to write the compilation log to
	"""

	# TODO: Implement Java compilation
	raise NotImplementedError('Java compilation is not implemented')
