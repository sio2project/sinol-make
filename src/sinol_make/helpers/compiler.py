import sinol_make.util as util
import sys, subprocess

def check_if_installed(compiler):
	"""
	Check if a compiler is installed
	"""

	try:
		subprocess.call([compiler, '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
	except FileNotFoundError:
		return False

	return True


def get_c_compiler_path():
	"""
	Get the C compiler
	"""

	if sys.platform == 'win32' or sys.platform == 'cygwin' or sys.platform == 'linux':
		if not check_if_installed('gcc'):
			return None
		else:
			return 'gcc'
	elif sys.platform == 'darwin':
		for i in [9, 10, 11]:
			compiler = 'gcc-' + str(i)
			if check_if_installed(compiler):
				return compiler

		return None

def get_cpp_compiler_path():
	"""
	Get the C++ compiler
	"""

	if sys.platform == 'win32' or sys.platform == 'cygwin' or sys.platform == 'linux':
		if not check_if_installed('g++'):
			return None
		else:
			return 'g++'
	elif sys.platform == 'darwin':
		for i in [9, 10, 11]:
			compiler = 'g++-' + str(i)
			if check_if_installed(compiler):
				return compiler

		return None

def get_python_interpreter_path():
	"""
	Get the Python interpreter
	"""

	if not check_if_installed('python3'):
		return None
	else:
		return 'python3'

def get_java_compiler_path():
	"""
	Get the Java compiler
	"""

	if not check_if_installed('javac'):
		return None
	else:
		return 'javac'
