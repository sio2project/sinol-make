# Modified version of https://sinol3.dasie.mimuw.edu.pl/oij/jury/package/-/blob/master/runner.py
# Author of the original code: Bartosz Kostka <kostka@oij.edu.pl>
# Version 0.6 (2021-08-29)

import os
import collections
import sys
import re
import math
import multiprocessing as mp
import yaml
from sinol_make.commands.Exceptions import RunCommandException
from sinol_make.interfaces.BaseCommand import BaseCommand
from sinol_make.interfaces.Exceptions import CompilationException
from sinol_make.helpers import compile, compiler
from sinol_make import util

class Command(BaseCommand):
	"""
	Class for running current task
	"""


	def get_name(self):
		return 'run'


	def configure_subparser(self, subparser):
		parser = subparser.add_parser(
			'run',
			help='Run current task',
			description='Run current task'
		)
		parser.add_argument('--programs', type=str, nargs='+',
							help='programs to be run, for example prog/abc{b,s}*.{cpp,py}')
		parser.add_argument('--tests', type=str, nargs='+',
							help='tests to be run, for example in/abc{0,1}*')
		parser.add_argument('--cpus', type=int,
							help=f'number of cpus to use, you have {mp.cpu_count()} avaliable')
		parser.add_argument('--tl', type=float, help='time limit (in s)')
		parser.add_argument('--ml', type=float, help='memory limit (in MB)')
		parser.add_argument('--hide_memory', dest='hide_memory', action='store_true',
							help='hide memory usage in report')
		parser.add_argument('--validate_subtasks',
							dest='validate_subtasks', action='store_true',
							help='validate subtasks defined in config.yml')
		parser.add_argument('--validate_programs',
							dest='validate_programs', action='store_true',
							help='validate programs in prog/ directory')
		parser.add_argument('--subtask_report', type=str,
							help='file to store report from subtask validation (in markdown)')
		parser.add_argument('--program_report', type=str,
							help='file to store report from program executions (in markdown)')
		parser.add_argument('--oiejq_path', type=str,
		      				help='path to oiejq executable (default: `~/.local/bin/oiejq`)')
		parser.add_argument('--c_compiler_path', type=str, default=compiler.get_c_compiler_path(),
		    				help='C compiler to use (default for Linux and Windows: gcc, default for Mac: gcc-{9-12})')
		parser.add_argument('--cpp_compiler_path', type=str, default=compiler.get_cpp_compiler_path(),
		    				help='C++ compiler to use (default for Linux and Windows: g++, default for Mac: gcc-{9-12})')
		parser.add_argument('--python_interpreter_path', type=str, default=compiler.get_python_interpreter_path(),
		    				help='Python interpreter to use (default: python3)')
		parser.add_argument('--java_compiler_path', type=str, default=compiler.get_java_compiler_path(),
		    				help='Java compiler to use (default: javac)')



	def color_memory(self, memory, limit):
		if memory == -1:
			return util.color_yellow("")
		memory_str = f'{memory / 1024.0:.1f}MB'
		if memory > limit:
			return util.color_red(memory_str)
		elif memory > limit / 2.0:
			return util.color_yellow(memory_str)
		else:
			return util.color_green(memory_str)


	def color_time(self, time, limit):
		if time == -1:
			return util.color_yellow("")
		time_str = f'{time / 1000.0:.2f}s'
		if time > limit:
			return util.color_red(time_str)
		elif time > limit / 2.0:
			return util.color_yellow(time_str)
		else:
			return util.color_green(time_str)


	def colorize_status(self, status):
		if status == "OK":
			return util.bold(util.color_green(status))
		if status == "  " or status == "??":
			return util.bold(util.color_yellow(status))
		return util.bold(util.color_red(status))


	def parse_time(self, time_str):
		if len(time_str) < 3:
			return -1
		return int(time_str[:-2])


	def parse_memory(self, memory_str):
		if len(memory_str) < 3:
			return -1
		return int(memory_str[:-2])


	def extract_test_no(self, test_path):
		return os.path.split(os.path.splitext(test_path)[0])[1][3:]


	def extract_program_name(self, program_path):
		return os.path.split(program_path)[1]


	def get_group(self, test_path):
		return int("".join(filter(str.isdigit, self.extract_test_no(test_path))))


	def get_test_key(self, test):
		return (self.get_group(test), test)


	def get_tests(self, arg_tests):
		if arg_tests is None:
			all_tests = [f'in/{test}' for test in os.listdir("in/")
						if test[-3:] == ".in"]
			return sorted(all_tests, key=self.get_test_key)
		else:
			return sorted(list(set(arg_tests)), key=self.get_test_key)


	def get_program_key(self, program):
		name = self.extract_program_name(program)
		value = [0, 0]
		if name[3] == 's':
			value[0] = 1
			suffix = name.split(".")[0][4:]
		elif name[3] == 'b':
			value[0] = 2
			suffix = name.split(".")[0][4:]
		else:
			suffix = name.split(".")[0][3:]
		if suffix != "":
			value[1] = int(suffix)
		return tuple(value)


	def get_programs(self, arg_problems):
		if arg_problems is None:
			all_programs = [program for program in os.listdir("prog/")
							if self.PROGRAMS_RE.match(program)]
			return sorted(all_programs, key=self.get_program_key)
		else:
			return sorted(list(set(arg_problems)), key=self.get_program_key)


	def get_possible_score(self, groups):
		possible_score = 0
		for group in groups:
			possible_score += self.scores[group]
		return possible_score

	def get_executable(self, program):
		return os.path.splitext(self.extract_program_name(program))[0] + ".e"


	def get_source_file(self, executable):
		file = os.path.splitext(executable)[0]
		for ext in self.SOURCE_EXTENSIONS:
			if os.path.isfile(file + ext):
				return file + ext
		raise RunCommandException(f'Source file not found for executable {executable}')


	def get_output_file(self, test_path):
		return os.path.join("out", os.path.split(os.path.splitext(test_path)[0])[1]) + ".out"


	def compile_programs(self, programs):
		os.makedirs(self.COMPILATION_DIR, exist_ok=True)
		os.makedirs(self.EXECUTABLES_DIR, exist_ok=True)
		print(f'Compiling {len(programs)} programs...')
		with mp.Pool(self.cpus) as pool:
			compilation_results = pool.map(self.compile, programs)
		if not all(compilation_results):
			print(util.bold(util.color_red("\nCompilation failed.")))
			exit(1)
		return compilation_results


	def compile(self, program):
		compile_log_file = os.path.join(
			self.COMPILATION_DIR, f'{self.extract_program_name(program)}.compile_log')
		source_file = self.get_source_file(os.path.join(os.getcwd(), "prog", program))
		output = os.path.join(self.EXECUTABLES_DIR, program)
		try:
			compile.compile(source_file, output, self.compilers, open(compile_log_file, "w", encoding="utf-8"))
			print(util.color_green(f'Compilation of file {self.extract_program_name(program)} was successful.'))
			return True
		except CompilationException:
			print(util.bold(util.color_red(f'Compilation of file {self.extract_program_name(program)} was unsuccessful.')))
			os.system("head -c 500 %s" % compile_log_file) # TODO: make this work on Windows
			return False


	def execute(self, execution):
		(name, program, test, time_limit, memory_limit, timetool_path) = execution
		output_file = os.path.join(self.EXECUTIONS_DIR, name,
								self.extract_test_no(test)+".out")
		result_file = os.path.join(self.EXECUTIONS_DIR, name,
								self.extract_test_no(test)+".res")
		hard_time_limit_in_s = math.ceil(2*time_limit / 1000.0)

		command = f'MEM_LIMIT={math.ceil(memory_limit)}K MEASURE_MEM=true' \
					f' timeout -k {hard_time_limit_in_s}s -s SIGKILL %d{hard_time_limit_in_s}s' \
					f'{timetool_path} {program}' \
					f'<{test} >{output_file} 2>{result_file}'
		code = os.system(command)
		result = {}
		with open(result_file, encoding='utf-8') as result:
			for line in result:
				line = line.strip()
				if ": " in line:
					(key, value) = line.split(": ")[:2]
					result[key] = value
		if "Time" in result.keys():
			result["Time"] = self.parse_time(result["Time"])
		if "Memory" in result.keys():
			result["Memory"] = self.parse_memory(result["Memory"])
		if code == 35072:
			result["Status"] = "TL"
		elif "Status" not in result.keys():
			result["Status"] = "RE"
		elif result["Status"] == "OK":
			if os.system(f'diff -q -Z {output_file} {self.get_output_file(test)} >/dev/null'):
				result["Status"] = "WA"
			elif result["Time"] > time_limit:
				result["Status"] = "TL"
			elif result["Memory"] > memory_limit:
				result["Status"] = "ML"
		else:
			result["Status"] = result["Status"][:2]
		return result

	def perform_executions(self, compiled_commands, names, programs, report_file):
		executions = []
		all_results = collections.defaultdict(
			lambda: collections.defaultdict(lambda: collections.defaultdict(map)))
		for (name, executable, result) in compiled_commands:
			if result:
				for test in self.tests:
					executions.append((name, executable, test, self.time_limit, self.memory_limit, self.timetool_path))
					all_results[name][self.get_group(test)][test] = {"Status": "  "}
				os.makedirs(os.path.join(self.EXECUTIONS_DIR, name), exist_ok=True)
			else:
				for test in self.tests:
					all_results[name][self.get_group(test)][test] = {"Status": "CE"}
		print()
		executions.sort(key = lambda x: (self.get_program_key(x[1]), x[2]))
		program_groups_scores = collections.defaultdict(dict)

		def print_view(output_file=None):
			if i != 0 and output_file is None:
				# TODO: always display both tables
				# if self.args.verbose:
				# 	cursor_delta = len(self.tests) + len(self.groups)+ 9
				# 	if not self.args.hide_memory:
				# 		cursor_delta += len(self.tests)
				# else:
				cursor_delta = len(self.groups) + 7
				number_of_rows = (len(programs) + self.PROGRAMS_IN_ROW - 1) // self.PROGRAMS_IN_ROW
				sys.stdout.write(f'\033[{cursor_delta * number_of_rows + 1}A')
			program_scores = collections.defaultdict(int)
			program_times = collections.defaultdict(lambda: -1)
			program_memory = collections.defaultdict(lambda: -1)
			if output_file is not None:
				sys.stdout = open(output_file, 'w', encoding='utf-8')
			else:
				time_remaining = (len(executions) - i - 1) * 2 * self.time_limit / self.cpus / 1000.0
				print(f'Done {i+1: >4}/{len(executions): >4}. Time remaining (in the worst case): {time_remaining: >5} seconds.')
			for program_ix in range(0, len(names), self.PROGRAMS_IN_ROW):
				# how to jump one line up
				program_group = names[program_ix:program_ix + self.PROGRAMS_IN_ROW]
				print("groups", end=" | ")
				for program in program_group:
					print(f'{program: >10}', end=" | ")
				print()
				print(6*"-", end=" | ")
				for program in program_group:
					print(10*"-", end=" | ")
				print()
				for group in self.groups:
					print('{group: >6}', end=" | ")
					for program in program_group:
						results = all_results[program][group]
						group_status = "OK"
						for test in results:
							status = results[test]["Status"]
							if "Time" in results[test].keys():
								program_times[program] = max(
									program_times[program], results[test]["Time"])
							elif status == "TL":
								program_times[program] = 2 * self.time_limit
							if "Memory" in results[test].keys():
								program_memory[program] = max(
									program_memory[program], results[test]["Memory"])
							elif status == "ML":
								program_memory[program] = 2 * self.memory_limit
							if status != "OK":
								group_status = status
								break
						print("%3s" % util.bold(util.color_green(group_status)) if group_status == "OK" else util.bold(util.color_red(group_status)),
							"%3s/%3s" % (self.scores[group] if group_status == "OK" else "---", self.scores[group]),
							end=" | ")
						program_scores[program] += self.scores[group] if group_status == "OK" else 0
						program_groups_scores[program][group] = group_status
					print()
				print(6*" ", end=" | ")
				for program in program_group:
					print(10*" ", end=" | ")
				print()
				print("points", end=" | ")
				for program in program_group:
					print(util.bold(f'   {program_scores[program]: >3}/{self.possible_score: >3}'), end=" | ")
				print()
				print("  time", end=" | ")
				for program in program_group:
					program_time = program_times[program]
					print(util.bold(("%20s" % self.color_time(program_time, self.time_limit))
						if program_time < 2 * self.time_limit and program_time >= 0
						else "   "+7*'-'), end=" | ")
				print()
				print("memory", end=" | ")
				for program in program_group:
					program_mem = program_memory[program]
					print(util.bold(("%20s" % self.color_memory(program_mem, self.memory_limit))
						if program_mem < 2 * self.memory_limit and program_mem >= 0
						else "   "+7*'-'), end=" | ")
				print()
				# TODO: always display both tables
				# if self.args.verbose:
				# 	print(6*" ", end=" | ")
				# 	for program in program_group:
				# 		print(10*" ", end=" | ")
				# 	print()
				# 	for test in self.tests:
				# 		print("%6s" % self.extract_test_no(test), end=" | ")
				# 		for program in program_group:
				# 			result = all_results[program][self.get_group(test)][test]
				# 			status = result["Status"]
				# 			if status == "  ": print(10*' ', end=" | ")
				# 			else:
				# 				print("%3s" % self.colorize_status(status),
				# 					("%17s" % self.color_time(result["Time"], self.time_limit)) if "Time" in result.keys() else 7*" ", end=" | ")
				# 		print()
				# 		if not self.args.hide_memory:
				# 			print(6*" ", end=" | ")
				# 			for program in program_group:
				# 				result = all_results[program][self.get_group(test)][test]
				# 				print(("%20s" % self.color_memory(result["Memory"], self.memory_limit))  if "Memory" in result.keys() else 10*" ", end=" | ")
				# 			print()
				# 	print()
				print(10*len(program_group)*' ')
			sys.stdout = sys.__stdout__
			if output_file is not None:
				os.system('sed -i -r "s/\x1B\[([0-9]{1,3}(;[0-9]{1,2})?)?[mGK]//g" %s' % output_file) # TODO: make this work on Windows
				print("Report has been saved to", util.bold(output_file))
				print()

		print(f'Performing {len(executions)} executions...')
		with mp.Pool(self.cpus) as pool:
			for i, result in enumerate(pool.imap(self.execute, executions)):
				(name, _, test) = executions[i][:3]
				all_results[name][self.get_group(test)][test] = result
				print_view()
		if report_file:
			print_view(report_file)
		return program_groups_scores


	def validate_subtasks(self):
		print("Validating subtasks...")
		if 'subtasks' not in self.config.keys():
			print(util.bold(util.color_red('Subtasks description not defined in config.yml.')))
			exit(1)

		programs = []
		for subtask in self.config["subtasks"]:
			score_checksum = 0
			for group in  self.config["subtasks"][subtask]["groups"]:
				if group not in self.scores.keys() or group == 0:
					print(util.bold(util.color_red(f'Group {group} was not defined.')))
					exit(1)

				score_checksum += self.scores[group]
			score_expected = self.config["subtasks"][subtask]["points"]
			if score_checksum != score_expected:
				print(util.bold(util.color_red(f'Subtask {subtask} will grant {score_checksum} points (expected {score_expected}).')))
				exit(1)

			validator_program = self.config["subtasks"][subtask]["validator"].split()[0]
			programs.append(validator_program)
		programs = list(set(programs))
		compilation_results = self.compile_programs(programs)
		os.makedirs(self.EXECUTIONS_DIR, exist_ok=True)
		compiled_commands = []
		for subtask in self.config["subtasks"]:
			validator_program = os.path.join(self.EXECUTABLES_DIR, self.config["subtasks"][subtask]["validator"])
			compiled_commands.append((subtask, validator_program, True))
		names = list(self.config["subtasks"])
		results = self.perform_executions(compiled_commands, names, programs, self.args.subtask_report)
		for subtask in self.config["subtasks"]:
			passed_groups = []
			for group in self.config["scores"]:
				if results[subtask][group] == "OK":
					passed_groups.append(group)
			passed_groups.sort()
			should_pass = self.config["subtasks"][subtask]["groups"]
			should_pass.sort()
			if passed_groups != should_pass:
				print(util.bold(util.color_red('Subtask %s will pass groups %s (expected %s).' % (subtask, passed_groups, should_pass))))
				exit(1)


	def run_programs(self):
		programs = self.get_programs(self.args.programs)
		print(f'The following {len(programs)} programs will be executed:\n'
			  f'{[self.extract_program_name(program) for program in programs]}')
		print(f'on the following {len(self.tests)} tests:\n'
			  f'{[self.extract_test_no(test) for test in self.tests]}')
		print(f'in parallel on {self.cpus} cpus.')
		print()
		compilation_results = self.compile_programs(programs)
		os.makedirs(self.EXECUTIONS_DIR, exist_ok=True)
		program_executables = [os.path.join(self.EXECUTABLES_DIR, self.get_executable(program))
							for program in programs]
		compiled_commands = zip(programs, program_executables, compilation_results)
		names = programs
		self.perform_executions(compiled_commands, names, programs, self.args.program_report)


	def run(self, args):
		if not util.check_if_project():
			print(util.bold(util.color_yellow('You are not in a project directory '
				    		'(couldn\'t find config.yml in current directory).')))
			exit(1)

		self.args = args
		self.config = yaml.load(open("config.yml", encoding='utf-8'), Loader=yaml.FullLoader)

		if not 'title' in self.config.keys():
			print(util.bold(util.color_red('Title was not defined in config.yml.')))
			exit(1)
		if not 'time_limit' in self.config.keys():
			print(util.bold(util.color_red('Time limit was not defined in config.yml.')))
			exit(1)
		if not 'memory_limit' in self.config.keys():
			print(util.bold(util.color_red('Memory limit was not defined in config.yml.')))
			exit(1)
		if not 'scores' in self.config.keys():
			print(util.bold(util.color_red('Scores were not defined in config.yml.')))
			exit(1)

		self.ID = os.path.split(os.getcwd())[-1]
		self.TMP_DIR = os.path.join(os.getcwd(), "cache")
		self.COMPILATION_DIR = os.path.join(self.TMP_DIR, "compilation")
		self.EXECUTIONS_DIR = os.path.join(self.TMP_DIR, "executions")
		self.EXECUTABLES_DIR = os.path.join(self.TMP_DIR, "executables")
		self.SOURCE_EXTENSIONS = ['.c', '.cpp', '.py', '.java']
		self.PROGRAMS_IN_ROW = 8
		self.PROGRAMS_RE = re.compile(r"^%s[bs]?[0-9]*\.(cpp|cc|java|py|pas)$" % self.ID)

		for program in self.get_programs(None):
			ext = os.path.splitext(program)[1]
			compiler = ""
			tried = ""
			flag = ""
			if ext == '.c' and args.c_compiler_path is None:
				compiler = 'C compiler'
				flag = '--c_compiler_path'
				if sys.platform == 'darwin':
					tried = 'gcc-{9,10,11,12}'
				else:
					tried = 'gcc'
			elif ext == '.cpp' and args.cpp_compiler_path is None:
				compiler = 'C++ compiler'
				flag = '--cpp_compiler_path'
				if sys.platform == 'darwin':
					tried = 'g++-{9,10,11,12}'
				else:
					tried = 'g++'
			elif ext == '.py' and args.python_intepreter_path:
				compiler = 'Python interpreter'
				tried = 'python3'
				flag = '--python_interpreter_path'
			elif ext == '.java' and args.java_compiler_path is None:
				compiler = 'Java compiler'
				tried = 'javac'
				flag = '--java_compiler_path'

			if compiler != "":
				print(util.bold(util.color_red(f'Couldn\'t find a {compiler}. Tried {tried}. '
				   							   f'Try specyfing it with {flag}.')))
				exit(1)

		self.compilers = {
			'c_compiler_path': args.c_compiler_path,
			'cpp_compiler_path': args.cpp_compiler_path,
			'python_interpreter_path': args.python_interpreter_path,
			'java_compiler_path': args.java_compiler_path
		}

		if 'oiejq_path' in args and args.oiejq_path is not None:
			if not util.check_oiejq(args.oiejq_path):
				print(util.bold(util.color_red('Invalid oiejq path.')))
				exit(1)
			self.timetool_path = args.oiejq_path
		else:
			self.timetool_path = util.get_oiejq_path()
		if self.timetool_path is None:
			print(util.bold(util.color_red('oiejq is not installed.')))
			exit(1)

		title = self.config["title"]
		print(f'Task {title} ({self.ID})')
		config_time_limit = self.config["time_limit"]
		config_memory_limit = self.config["memory_limit"]
		self.time_limit = args.tl * 1000.0 if args.tl is not None else config_time_limit
		self.memory_limit = args.ml * 1024.0 if args.ml is not None else config_memory_limit
		self.cpus = args.cpus or mp.cpu_count()
		if self.time_limit == config_time_limit:
			print("Time limit (in ms):", self.time_limit)
		else:
			print("Time limit (in ms):", self.time_limit,
				util.bold(util.color_yellow(f'[originally was {config_time_limit:.1f} ms]')))
		if self.memory_limit == config_memory_limit:
			print("Memory limit (in kb):", self.memory_limit)
		else:
			print("Memory limit (in kb):", self.memory_limit,
				util.bold(util.color_yellow((f'[originally was {config_memory_limit:.1f} kb]'))))
		self.scores = collections.defaultdict(int)
		print("Scores:")
		total_score = 0
		for group in self.config["scores"]:
			self.scores[group] = self.config["scores"][group]
			print(f'{group: >2}: {self.scores[group]: >3}')
			total_score += self.scores[group]
		if total_score != 100:
			print(util.bold(util.color_yellow(f'WARN: Scores sum up to {total_score} (instead of 100).')))
		print()

		self.tests = self.get_tests(args.tests)
		self.groups = list(sorted(set([self.get_group(test) for test in self.tests])))
		self.possible_score = self.get_possible_score(self.groups)

		if args.validate_subtasks:
			self.validate_subtasks()
		elif args.validate_programs:
			self.run_programs()
		else:
			self.validate_subtasks()
			self.run_programs()
