import sinol_make.helpers.compiler as compiler
from sinol_make.interfaces.Errors import CompilationError
import os, subprocess, sys

def compile(program, output, compilers = None, compile_log = None):
	"""
	Compile a program
	compilers - A dictionary of compilers to use. If not set, the default compilers will be used
	"""
	ext = os.path.splitext(program)[1]

	if ext == '.cpp':
		compile_cpp(program, output, (compilers['cpp_compiler'] or compiler.get_cpp_compiler()), compile_log)
	elif ext == '.c':
		compile_c(program, output, (compilers['c_compiler'] or compiler.get_c_compiler()), compile_log)
	elif ext == '.py':
		compile_python(program, output, (compilers['python_interpreter'] or compiler.get_python_interpreter()), compile_log)
	elif ext == '.java':
		compile_java(program, output, (compilers['java_compiler'] or compiler.get_java_compiler()), compile_log)
	else:
		raise CompilationError('Unknown file extension: ' + ext)


def compile_c(program, output, compiler_path, compile_log = None):
	"""
	Compile a C program
	compile_log - A file to write the compilation log to
	"""
	
	flags = '-O3 -lm -Werror -Wall -Wextra -Wshadow -Wconversion -Wno-unused-result -Wfloat-equal'.split(' ')
	
	process = subprocess.Popen([compiler_path, program, '-o', output] + flags, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
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


def compile_cpp(program, output, compiler_path, compile_log = None):
	"""
	Compile a C++ program.
	compile_log - A file to write the compilation log to
	"""

	flags = '-O3 -lm -Werror -Wall -Wextra -Wshadow -Wconversion -Wno-unused-result -Wfloat-equal'.split(' ')
	
	process = subprocess.Popen([compiler_path, program, '-o', output] + flags, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
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


def compile_python(program, output, compiler_path, compile_log = None):
	"""
	Compile a Python program
	compile_log - A file to write the compilation log to
	"""

	if sys.platform == 'win32' or sys.platform == 'cygwin':
		# TODO: Make this work on Windows
		pass
	else:
		open(output, 'w').write('#!/usr/bin/python3\n')
		open(output, 'a').write(open(program, 'r').read())
		subprocess.call(['chmod', '+x', output])
	
	process = subprocess.Popen([compiler_path, '-m', 'compileall', output], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
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
	
def compile_java(program, output, compiler_path, compile_log = None):
	"""
	Compile a Java program
	compile_log - A file to write the compilation log to
	"""

	# TODO: Implement Java compilation
	raise NotImplementedError('Java compilation is not implemented')
