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


def get_c_compiler(args = None):
	"""
	Get the C compiler
	args - ArgParser arguments. Used to get compiler flags if set
	"""

	if 'c_compiler' in args and args.c_compiler is not None:
		if not check_if_installed(args.c_compiler):
			print(util.bold(util.color_red('C compiler \'' + args.c_compiler + '\' not found. You can set the C compiler with --c_compiler flag')))
			exit(1)
		else:
			return args.c_compiler
		
	if sys.platform == 'win32' or sys.platform == 'linux':
		if not check_if_installed('gcc'):
			print(util.bold(util.color_red('C compiler \'gcc\' not found. You can set the C compiler with --c_compiler flag')))
			exit(1)
		else:
			return 'gcc'
	elif sys.platform == 'darwin':
		for i in range(9, 13):
			compiler = 'gcc-' + str(i)
			if check_if_installed(compiler):
				return compiler
			
		print(util.bold(util.color_red('C compiler not found. You can set the C compiler with --c_compiler flag')))
		exit(1)

def get_cpp_compiler(args = None):
	"""
	Get the C++ compiler
	args - ArgParser arguments. Used to get compiler flags if sets
	"""

	if 'cpp_compiler' in args and args.cpp_compiler is not None:
		if not check_if_installed(args.cpp_compiler):
			print(util.bold(util.color_red('C++ compiler \'' + args.cpp_compiler + '\' not found. You can set the C++ compiler with --cpp_compiler flag')))
			exit(1)
		else:
			return args.cpp_compiler
		
	if sys.platform == 'win32' or sys.platform == 'linux':
		if not check_if_installed('g++'):
			print(util.bold(util.color_red('C++ compiler \'g++\' not found. You can set the C++ compiler with --cpp_compiler flag')))
			exit(1)
		else:
			return 'g++'
	elif sys.platform == 'darwin':
		for i in range(9, 13):
			compiler = 'g++-' + str(i)
			if check_if_installed(compiler):
				return compiler
			
		print(util.bold(util.color_red('C++ compiler not found. You can set the C++ compiler with --cpp_compiler flag')))
		exit(1)

def get_python_interpreter(args = None):
	"""
	Get the Python interpreter
	args - ArgParser arguments. Used to get interpreter flags if set
	"""

	if 'python_interpreter' in args and args.python_interpreter is not None:
		if not check_if_installed(args.python_interpreter):
			print(util.bold(util.color_red('Python interpreter \'' + args.python_interpreter + '\' not found. You can set the Python interpreter with --python_interpreter flag')))
			exit(1)
		else:
			return args.python_interpreter
		
	if not check_if_installed('python3'):
		print(util.bold(util.color_red('Python interpreter \'python3\' not found. You can set the Python interpreter with --python_interpreter flag')))
		exit(1)
	else:
		return 'python3'
	
def get_java_compiler(args = None):
	"""
	Get the Java compiler
	args - ArgParser arguments. Used to get compiler flags if set
	"""

	if 'java_compiler' in args and args.java_compiler is not None:
		if not check_if_installed(args.java_compiler):
			print(util.bold(util.color_red('Java compiler \'' + args.java_compiler + '\' not found. You can set the Java compiler with --java_compiler flag')))
			exit(1)
		else:
			return args.java_compiler
		
	if not check_if_installed('javac'):
		print(util.bold(util.color_red('Java compiler \'javac\' not found. You can set the Java compiler with --java_compiler flag')))
		exit(1)
	else:
		return 'javac'
