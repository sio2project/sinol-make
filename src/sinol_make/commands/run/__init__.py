# Modified version of https://sinol3.dasie.mimuw.edu.pl/oij/jury/package/-/blob/master/runner.py
# Author of the original code: Bartosz Kostka <kostka@oij.edu.pl>
# Version 0.6 (2021-08-29)

from sinol_make.commands.run.structs import ExecutionResult, ResultChange, ValidationResult, ExecutionData
from sinol_make.interfaces.BaseCommand import BaseCommand
from sinol_make.interfaces.Errors import CompilationError
from sinol_make.helpers import compile, compiler
import sinol_make.util as util
import yaml, os, collections, sys, re, math, dictdiffer
import multiprocessing as mp

class Command(BaseCommand):
	"""
	Class for running current task
	"""


	def get_name(self):
		return 'run'


	def configure_subparser(self, subparser):
		parser = subparser.add_parser(
			'run',
			help='Runs solutions in parallel on tests and verifies the expected solutions\' scores with the config.',
			description='Runs selected solutions (by default all solutions) \
				on selected tests (by default all tests) \
				with a given number of cpus. \
				Measures the solutions\' time with oiejq, unless specified otherwise. \
				After running the solutions, it compares the solutions\' scores with the ones saved in config.yml.'
		)

		default_timetool = 'oiejq' if sys.platform == 'linux' else 'time'

		parser.add_argument('--solutions', type=str, nargs='+',
							help='solutions to be run, for example prog/abc{b,s}*.{cpp,py}')
		parser.add_argument('--tests', type=str, nargs='+',
							help='tests to be run, for example in/abc{0,1}*')
		parser.add_argument('--cpus', type=int,
							help='number of cpus to use, you have %d avaliable' % mp.cpu_count())
		parser.add_argument('--tl', type=float, help='time limit (in s)')
		parser.add_argument('--ml', type=float, help='memory limit (in MB)')
		parser.add_argument('--hide_memory', dest='hide_memory', action='store_true',
							help='hide memory usage in report')
		parser.add_argument('--solutions_report', type=str,
							help='file to store report from solution executions (in markdown)')
		parser.add_argument('--time_tool', choices=['oiejq', 'time'], default=default_timetool,
		      				help='tool to measure time and memory usage (default when possible: oiejq)')
		parser.add_argument('--oiejq_path', type=str,
		      				help='path to oiejq executable (default: `~/.local/bin/oiejq`)')
		parser.add_argument('--c_compiler_path', type=str, default=compiler.get_c_compiler_path(),
		    				help='C compiler to use (default for Linux and Windows: gcc, default for Mac: gcc-9 or gcc-10)')
		parser.add_argument('--cpp_compiler_path', type=str, default=compiler.get_cpp_compiler_path(),
		    				help='C++ compiler to use (default for Linux and Windows: g++, default for Mac: g++-9 or g++-10)')
		parser.add_argument('--python_interpreter_path', type=str, default=compiler.get_python_interpreter_path(),
		    				help='Python interpreter to use (default: python3)')
		parser.add_argument('--java_compiler_path', type=str, default=compiler.get_java_compiler_path(),
		    				help='Java compiler to use (default: javac)')
		parser.add_argument('--apply_suggestions', dest='apply_suggestions', action='store_true',
		      				help='apply suggestions from expected scores report')


	def color_memory(self, memory, limit):
		if memory == -1: return util.color_yellow("")
		memory_str = "%.1fMB" % (memory / 1024.0)
		if memory > limit: return util.color_red(memory_str)
		elif memory > limit / 2.0: return util.color_yellow(memory_str)
		else: return util.color_green(memory_str)


	def color_time(self, time, limit):
		if time == -1: return util.color_yellow("")
		time_str = "%.2fs" % (time / 1000.0)
		if time > limit: return util.color_red(time_str)
		elif time > limit / 2.0: return util.color_yellow(time_str)
		else: return util.color_green(time_str)


	def colorize_status(self, status):
		if status == "OK": return util.bold(util.color_green(status))
		if status == "  " or status == "??": return util.warning(status)
		return util.error(status)


	def parse_time(self, time_str):
		if len(time_str) < 3: return -1
		return int(time_str[:-2])


	def parse_memory(self, memory_str):
		if len(memory_str) < 3: return -1
		return int(memory_str[:-2])


	def extract_test_no(self, test_path):
		return os.path.split(os.path.splitext(test_path)[0])[1][3:]


	def extract_file_name(self, file_path):
		return os.path.split(file_path)[1]


	def get_group(self, test_path):
		return int("".join(filter(str.isdigit, self.extract_test_no(test_path))))


	def get_test_key(self, test):
		return (self.get_group(test), test)


	def get_tests(self, arg_tests):
		if arg_tests is None:
			all_tests = ["in/%s" % test for test in os.listdir("in/")
						if test[-3:] == ".in"]
			return sorted(all_tests, key=self.get_test_key)
		else:
			return sorted(list(set(arg_tests)), key=self.get_test_key)


	def get_executable_key(self, executable):
		name = self.extract_file_name(executable)
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


	def get_solution_from_exe(self, executable):
		file = os.path.splitext(executable)[0]
		for ext in self.SOURCE_EXTENSIONS:
			if os.path.isfile(os.path.join(os.getcwd(), "prog", file + ext)):
				return file + ext
		util.exit_with_error("Source file not found for executable %s" % executable)


	def get_solutions(self, args_solutions):
		if args_solutions is None:
			solutions = [solution for solution in os.listdir("prog/")
							if self.SOLUTIONS_RE.match(solution)]
			return sorted(solutions, key=self.get_executable_key)
		else:
			solutions = []
			for solution in args_solutions:
				if not os.path.isfile(solution):
					util.exit_with_error("Solution %s does not exist" % solution)
				solutions.append(os.path.basename(solution))
			return sorted(solutions, key=self.get_executable_key)


	def get_executable(self, file):
		return os.path.splitext(self.extract_file_name(file))[0] + ".e"


	def get_executables(self, args_solutions):
		return [os.get_executable(solution) for solution in self.get_solutions(args_solutions)]


	def get_possible_score(self, groups):
		possible_score = 0
		for group in groups:
			possible_score += self.scores[group]
		return possible_score


	def get_output_file(self, test_path):
		return os.path.join("out", os.path.split(os.path.splitext(test_path)[0])[1]) + ".out"


	def compile_solutions(self, solutions):
		os.makedirs(self.COMPILATION_DIR, exist_ok=True)
		os.makedirs(self.EXECUTABLES_DIR, exist_ok=True)
		print("Compiling %d solutions..." % len(solutions))
		with mp.Pool(self.cpus) as pool:
			compilation_results = pool.map(self.compile, solutions)
		if not all(compilation_results):
			util.exit_with_error("\nCompilation failed.")
		return compilation_results


	def compile(self, solution):
		compile_log_file = os.path.join(
			self.COMPILATION_DIR, "%s.compile_log" % self.extract_file_name(solution))
		source_file = os.path.join(os.getcwd(), "prog", self.get_solution_from_exe(solution))
		output = os.path.join(self.EXECUTABLES_DIR, self.get_executable(solution))
		try:
			compile.compile(source_file, output, self.compilers, open(compile_log_file, "w"))
			print(util.info("Compilation of file %s was successful."
							% self.extract_file_name(solution)))
			return True
		except CompilationError as e:
			print(util.error("Compilation of file %s was unsuccessful."
								% self.extract_file_name(solution)))
			os.system("head -c 500 %s" % compile_log_file) # TODO: make this work on Windows
			return False


	def execute_oiejq(self, command, result_file, output_file, answer_file, time_limit, memory_limit):
		timeout_exit_code = os.system(command)
		result = ExecutionResult(None, None, None)
		with open(result_file) as r:
			for line in r:
				line = line.strip()
				if ": " in line:
					(key, value) = line.split(": ")[:2]
					if key == "Time":
						result.Time = self.parse_time(value)
					elif key == "Memory":
						result.Memory = self.parse_memory(value)
					else:
						setattr(result, key, value)

		if timeout_exit_code == 35072:
			result.Status = "TL"
		elif getattr(result, "Time") is not None and result.Time > time_limit:
			result.Status = "TL"
		elif getattr(result, "Memory") is not None and result.Memory > memory_limit:
			result.Status = "ML"
		elif getattr(result, "Status") is None:
			result.Status = "RE"
		elif result.Status == "OK":
			if result.Time > time_limit:
				result.Status = "TL"
			elif result.Memory > memory_limit:
				result.Status = "ML"
			elif os.system("diff -q -Z %s %s >/dev/null"
						% (output_file, answer_file)):
				result.Status = "WA"
		else:
			result.Status = result.Status[:2]

		return result


	def execute_time(self, command, result_file, output_file, answer_file, time_limit, memory_limit):
		timeout_exit_code = os.system(command)

		result = ExecutionResult(None, None, None)
		lines = open(result_file).readlines()
		program_exit_code = None
		if len(lines) == 3:
			"""
			If programs runs successfully, the output looks like this:
			 - first line is CPU time in seconds
			 - second line is memory in KB
			 - third line is exit code
			This format is defined by -f flag in time command.
			"""
			result.Time = round(float(lines[0].strip()) * 1000)
			result.Memory = int(lines[1].strip())
			program_exit_code = int(lines[2].strip())
		if len(lines) > 0 and "Command terminated by signal " in lines[0]:
			"""
			If there was a runtime error, the first line is the error message with signal number.
			For example:
				Command terminated by signal 11
			"""
			program_exit_code = int(lines[0].strip().split(" ")[-1])

		if program_exit_code != None and program_exit_code != 0:
			result.Status = "RE"
		elif timeout_exit_code != 0:
			result.Status = "TL"
		elif result.Time > time_limit:
			result.Status = "TL"
		elif result.Memory > memory_limit:
			result.Status = "ML"
		elif os.system("diff -q -Z %s %s >/dev/null" % (output_file, answer_file)):
			result.Status = "WA"
		else:
			result.Status = "OK"

		return result


	def run_solution(self, data_for_execution: ExecutionData):
		"""
		Run an execution and return the result as ExecutionResult object.
		"""

		(name, executable, test, time_limit, memory_limit, timetool_path) = data_for_execution
		file_no_ext = os.path.join(self.EXECUTIONS_DIR, name, self.extract_test_no(test))
		output_file = file_no_ext + ".out"
		result_file = file_no_ext + ".res"
		hard_time_limit_in_s = math.ceil(2 * time_limit / 1000.0)

		if self.args.time_tool == 'oiejq':
			command = "MEM_LIMIT=%sK MEASURE_MEM=true timeout -k %ds -s SIGKILL %ds %s %s <%s >%s 2>%s" \
					% (memory_limit, hard_time_limit_in_s,
						hard_time_limit_in_s, timetool_path,
						executable, test, output_file, result_file)

			return self.execute_oiejq(command, result_file, output_file, self.get_output_file(test), time_limit, memory_limit)
		elif self.args.time_tool == 'time':
			if sys.platform == 'darwin':
				timeout_name = 'gtimeout'
				time_name = 'gtime'
			elif sys.platform == 'linux':
				timeout_name = 'timeout'
				time_name = 'time'
			elif sys.platform == 'win32' or sys.platform == 'cygwin':
				raise Exception("Measuring time with GNU time on Windows is not supported.")

			command = f'{timeout_name} -k {hard_time_limit_in_s}s {hard_time_limit_in_s}s ' \
						f'{time_name} -f "%U\\n%M\\n%x" -o {result_file} {executable} <{test} >{output_file}'
			return self.execute_time(command, result_file, output_file, self.get_output_file(test), time_limit, memory_limit)


	def update_group_status(self, group_status, new_status):
		order = ["TL", "ML", "RE", "WA", "OK"]
		if order.index(new_status) < order.index(group_status):
			return new_status
		return group_status

	def run_solutions(self, compiled_commands, names, solutions, report_file):
		"""
		Run solutions on tests and print the results as a table to stdout.
		"""

		executions = []
		all_results = collections.defaultdict(
			lambda: collections.defaultdict(lambda: collections.defaultdict(map)))
		for (name, executable, result) in compiled_commands:
			if result:
				for test in self.tests:
					executions.append((name, executable, test, self.time_limit, self.memory_limit, self.timetool_path))
					all_results[name][self.get_group(test)][test] = ExecutionResult("  ", None, None)
				os.makedirs(os.path.join(self.EXECUTIONS_DIR, name), exist_ok=True)
			else:
				for test in self.tests:
					all_results[name][self.get_group(test)][test] = ExecutionResult("CE", None, None)
		print()
		executions.sort(key = lambda x: (self.get_executable_key(x[1]), x[2]))
		program_groups_scores = collections.defaultdict(dict)

		def print_view(output_file=None):
			def print_stream(*values, end='\n'):
				if output_file is not None:
					print(*values, end=end, file=output_file)
				else:
					print(*values, end=end)

			if i != 0 and output_file is None:
				# TODO: always display both tables
				# if self.args.verbose:
				# 	cursor_delta = len(self.tests) + len(self.groups)+ 9
				# 	if not self.args.hide_memory:
				# 		cursor_delta += len(self.tests)
				# else:
				cursor_delta = len(self.groups) + 7
				number_of_rows = (len(solutions) + self.PROGRAMS_IN_ROW - 1) // self.PROGRAMS_IN_ROW
				sys.stdout.write('\033[%dA' % (cursor_delta * number_of_rows + 1))
			program_scores = collections.defaultdict(int)
			program_times = collections.defaultdict(lambda: -1)
			program_memory = collections.defaultdict(lambda: -1)
			if output_file is None:
				time_remaining = (len(executions) - i - 1) * 2 * self.time_limit / self.cpus / 1000.0
				print_stream('Done %4d/%4d. Time remaining (in the worst case): %5d seconds.'
					% (i+1, len(executions), time_remaining))
			for program_ix in range(0, len(names), self.PROGRAMS_IN_ROW):
				# how to jump one line up
				program_group = names[program_ix:program_ix + self.PROGRAMS_IN_ROW]
				print_stream("groups", end=" | ")
				for program in program_group:
					print_stream("%10s" % program, end=" | ")
				print_stream()
				print_stream(6*"-", end=" | ")
				for program in program_group:
					print_stream(10*"-", end=" | ")
				print_stream()
				for group in self.groups:
					print_stream("%6s" % group, end=" | ")
					for program in program_group:
						results = all_results[program][group]
						group_status = "OK"
						for test in results:
							status = results[test].Status
							if getattr(results[test], "Time") is not None:
								program_times[program] = max(
									program_times[program], results[test].Time)
							elif status == "TL":
								program_times[program] = 2 * self.time_limit
							if getattr(results[test], "Memory") is not None:
								program_memory[program] = max(
									program_memory[program], results[test].Memory)
							elif status == "ML":
								program_memory[program] = 2 * self.memory_limit
							if status == "  ":
								group_status = "  "
							else:
								group_status = self.update_group_status(group_status, status)

						print_stream("%3s" % util.bold(util.color_green(group_status)) if group_status == "OK" else util.bold(util.color_red(group_status)),
							"%3s/%3s" % (self.scores[group] if group_status == "OK" else "---", self.scores[group]),
							end=" | ")
						program_scores[program] += self.scores[group] if group_status == "OK" else 0
						program_groups_scores[program][group] = group_status
					print_stream()
				print_stream(6*" ", end=" | ")
				for program in program_group:
					print_stream(10*" ", end=" | ")
				print_stream()
				print_stream("points", end=" | ")
				for program in program_group:
					print_stream(util.bold("   %3s/%3s" % (program_scores[program], self.possible_score)), end=" | ")
				print_stream()
				print_stream("  time", end=" | ")
				for program in program_group:
					program_time = program_times[program]
					print_stream(util.bold(("%20s" % self.color_time(program_time, self.time_limit))
						if program_time < 2 * self.time_limit and program_time >= 0
						else "   "+7*'-'), end=" | ")
				print_stream()
				print_stream("memory", end=" | ")
				for program in program_group:
					program_mem = program_memory[program]
					print_stream(util.bold(("%20s" % self.color_memory(program_mem, self.memory_limit))
						if program_mem < 2 * self.memory_limit and program_mem >= 0
						else "   "+7*'-'), end=" | ")
				print_stream()
				# TODO: always display both tables
				# if self.args.verbose:
				# 	print_stream(6*" ", end=" | ")
				# 	for program in program_group:
				# 		print_stream(10*" ", end=" | ")
				# 	print_stream()
				# 	for test in self.tests:
				# 		print_stream("%6s" % self.extract_test_no(test), end=" | ")
				# 		for program in program_group:
				# 			result = all_results[program][self.get_group(test)][test]
				# 			status = result.Status
				# 			if status == "  ": print_stream(10*' ', end=" | ")
				# 			else:
				# 				print_stream("%3s" % self.colorize_status(status),
				# 					("%17s" % self.color_time(result.Time, self.time_limit)) if getattr(result, "Time") is not None else 7*" ", end=" | ")
				# 		print_stream()
				# 		if not self.args.hide_memory:
				# 			print_stream(6*" ", end=" | ")
				# 			for program in program_group:
				# 				result = all_results[program][self.get_group(test)][test]
				# 				print_stream(("%20s" % self.color_memory(result.Memory, self.memory_limit))  if getattr(result, "Memory") is not None else 10*" ", end=" | ")
				# 			print_stream()
				# 	print_stream()
				print_stream(10*len(program_group)*' ')

			if output_file is not None:
				os.system('sed -i -r "s/\x1B\[([0-9]{1,3}(;[0-9]{1,2})?)?[mGK]//g" %s' % output_file) # TODO: make this work on Windows
				print("Report has been saved to", util.bold(output_file))
				print()

		print("Performing %d executions..." % len(executions))
		with mp.Pool(self.cpus) as pool:
			for i, result in enumerate(pool.imap(self.run_solution, executions)):
				(name, executable, test) = executions[i][:3]
				all_results[name][self.get_group(test)][test] = result
				print_view()
		if report_file:
			print_view(report_file)
		return program_groups_scores


	def calculate_points(self, results):
		points = 0
		for group, result in results.items():
			if group != 0 and group not in self.config["scores"]:
				util.exit_with_error(f'Group {group} doesn\'t have points specified in config file.')
			if result == "OK" and group != 0:
				points += self.config["scores"][group]
		return points


	def compile_and_run(self, solutions):
		compilation_results = self.compile_solutions(solutions)
		os.makedirs(self.EXECUTIONS_DIR, exist_ok=True)
		executables = [os.path.join(self.EXECUTABLES_DIR, self.get_executable(solution))
							for solution in solutions]
		compiled_commands = zip(solutions, executables, compilation_results)
		names = solutions
		return self.run_solutions(compiled_commands, names, solutions, self.args.solutions_report)


	def print_expected_scores(self, expected_scores):
		yaml_dict = { "sinol_expected_scores": expected_scores }
		print(yaml.dump(yaml_dict, default_flow_style=None))


	def validate_expected_scores(self, results):
		new_expected_scores = {} # Expected scores based on results

		for solution in results.keys():
			new_expected_scores[solution] = {
				"expected": results[solution],
				"points": self.calculate_points(results[solution])
			}

		config_expected_scores = self.config.get("sinol_expected_scores", {})
		used_solutions = results.keys()
		if self.args.solutions == None and config_expected_scores: # If no solutions were specified, use all solutions from config
			used_solutions = config_expected_scores.keys()

		used_groups = set()
		if self.args.tests == None and config_expected_scores: # If no groups were specified, use all groups from config
			for solution in config_expected_scores.keys():
				for group in config_expected_scores[solution]["expected"]:
					used_groups.add(group)
		else:
			for solution in results.keys():
				for group in results[solution].keys():
					used_groups.add(group)
		used_groups = list(used_groups)

		expected_scores = {} # Expected scores from config with only solutions and groups that were run
		for solution in used_solutions:
			if solution in config_expected_scores.keys():
				expected_scores[solution] = {
					"expected": {},
					"points": 0
				}

				for group in used_groups:
					if group in config_expected_scores[solution]["expected"]:
						expected_scores[solution]["expected"][group] = config_expected_scores[solution]["expected"][group]

				expected_scores[solution]["points"] = self.calculate_points(expected_scores[solution]["expected"])

		print(util.bold("Expected scores from config:"))
		self.print_expected_scores(expected_scores)
		print(util.bold("\nExpected scores based on results:"))
		self.print_expected_scores(new_expected_scores)

		expected_scores_diff = dictdiffer.diff(expected_scores, new_expected_scores)
		added_solutions = set()
		removed_solutions = set()
		added_groups = set()
		removed_groups = set()
		changes = []

		for type, field, change in list(expected_scores_diff):
			if type == "add":
				if field == '': # Solutions were added
					for solution in change:
						added_solutions.add(solution[0])
				elif field[1] == "expected": # Groups were added
					for group in change:
						added_groups.add(group[0])
			elif type == "remove":
				# We check whether a solution was removed only when sinol_make was run on all of them
				if field == '' and self.args.solutions == None and config_expected_scores:
					for solution in change:
						removed_solutions.add(solution[0])
				# We check whether a group was removed only when sinol_make was run on all of them
				elif field[1] == "expected" and self.args.tests == None and config_expected_scores:
					for group in change:
						removed_groups.add(group[0])
			elif type == "change":
				if field[1] == "expected": # Results for at least one group has changed
					solution = field[0]
					group = field[2]
					old_result = change[0]
					result = change[1]
					changes.append(ResultChange(solution, group, old_result, result))

		return ValidationResult(
			added_solutions,
			removed_solutions,
			added_groups,
			removed_groups,
			changes,
			expected_scores,
			new_expected_scores
		)


	def print_expected_scores_diff(self, validation_results: ValidationResult):
		diff = validation_results
		config_expected_scores = self.config.get("sinol_expected_scores", {})

		def warn_if_not_empty(set, message):
			if len(set) > 0:
				print(util.warning(message + ": "), end='')
				print(util.warning(", ".join([str(x) for x in set])))

		warn_if_not_empty(diff.added_solutions, "Solutions were added")
		warn_if_not_empty(diff.removed_solutions, "Solutions were removed")
		warn_if_not_empty(diff.added_groups, "Groups were added")
		warn_if_not_empty(diff.removed_groups, "Groups were removed")

		for change in diff.changes:
			print(util.warning("Solution %s passed group %d with status %s while it should pass with status %s." %
										(change.solution, change.group, change.result, change.old_result)))

		if diff.expected_scores == diff.new_expected_scores:
			print(util.info("Expected scores are correct!"))
		else:
			def delete_group(solution, group):
				if group in config_expected_scores[solution]["expected"]:
					del config_expected_scores[solution]["expected"][group]
					config_expected_scores[solution]["points"] = self.calculate_points(config_expected_scores[solution]["expected"])

			def set_group_result(solution, group, result):
				config_expected_scores[solution]["expected"][group] = result
				config_expected_scores[solution]["points"] = self.calculate_points(config_expected_scores[solution]["expected"])


			if self.args.apply_suggestions:
				for solution in diff.removed_solutions:
					del config_expected_scores[solution]

				for solution in config_expected_scores:
					for group in diff.removed_groups:
						delete_group(solution, group)

				for solution in diff.new_expected_scores.keys():
					if solution in config_expected_scores:
						for group, result in diff.new_expected_scores[solution]["expected"].items():
							set_group_result(solution, group, result)
					else:
						config_expected_scores[solution] = diff.new_expected_scores[solution]


				self.config["sinol_expected_scores"] = config_expected_scores
				util.save_config(self.config)
				print(util.info("Saved suggested expected scores description."))
			else:
				util.exit_with_error("Use flag --apply_suggestions to apply suggestions.")


	def set_constants(self):
		self.ID = os.path.split(os.getcwd())[-1]
		self.TMP_DIR = os.path.join(os.getcwd(), "cache")
		self.COMPILATION_DIR = os.path.join(self.TMP_DIR, "compilation")
		self.EXECUTIONS_DIR = os.path.join(self.TMP_DIR, "executions")
		self.EXECUTABLES_DIR = os.path.join(self.TMP_DIR, "executables")
		self.SOURCE_EXTENSIONS = ['.c', '.cpp', '.py', '.java']
		self.PROGRAMS_IN_ROW = 8
		self.SOLUTIONS_RE = re.compile(r"^%s[bs]?[0-9]*\.(cpp|cc|java|py|pas)$" % self.ID)


	def validate_arguments(self, args):
		for solution in self.get_solutions(None):
			ext = os.path.splitext(solution)[1]
			compiler = ""
			tried = ""
			flag = ""
			if ext == '.c' and args.c_compiler_path is None:
				compiler = 'C compiler'
				flag = '--c_compiler_path'
				if sys.platform == 'darwin':
					tried = 'gcc-{9,10}'
				else:
					tried = 'gcc'
			elif ext == '.cpp' and args.cpp_compiler_path is None:
				compiler = 'C++ compiler'
				flag = '--cpp_compiler_path'
				if sys.platform == 'darwin':
					tried = 'g++-{9,10}'
				else:
					tried = 'g++'
			elif ext == '.py' and args.python_interpreter_path is None:
				compiler = 'Python interpreter'
				flag = '--python_interpreter_path'
				tried = 'python3'
			elif ext == '.java' and args.java_compiler_path is None:
				compiler = 'Java compiler'
				flag = '--java_compiler_path'
				tried = 'javac'

			if compiler != "":
				util.exit_with_error('Couldn\'t find a %s. Tried %s. Try specifying a compiler with %s.' % (compiler, tried, flag))

		compilers = {
			'c_compiler_path': args.c_compiler_path,
			'cpp_compiler_path': args.cpp_compiler_path,
			'python_interpreter_path': args.python_interpreter_path,
			'java_compiler_path': args.java_compiler_path
		}

		timetool_path = None
		if args.time_tool == 'oiejq':
			if sys.platform != 'linux':
				util.exit_with_error('oiejq is only available on Linux.')
			if 'oiejq_path' in args and args.oiejq_path is not None:
				if not util.check_oiejq(args.oiejq_path):
					util.exit_with_error('Invalid oiejq path.')
				timetool_path = args.oiejq_path
			else:
				timetool_path = util.get_oiejq_path()
			if timetool_path is None:
				util.exit_with_error('oiejq is not installed.')
		elif args.time_tool == 'time':
			if sys.platform == 'win32' or sys.platform == 'cygwin':
				util.exit_with_error('Measuring with `time` is not supported on Windows.')
			timetool_path = 'time'

		return compilers, timetool_path

	def run(self, args):
		if not util.check_if_project():
			print(util.warning('You are not in a project directory (couldn\'t find config.yml in current directory).'))
			exit(1)

		self.set_constants()
		self.args = args
		try:
			self.config = yaml.load(open("config.yml"), Loader=yaml.FullLoader)
		except AttributeError:
			self.config = yaml.load(open("config.yml"))

		if not 'title' in self.config.keys():
			util.exit_with_error('Title was not defined in config.yml.')
		if not 'time_limit' in self.config.keys():
			util.exit_with_error('Time limit was not defined in config.yml.')
		if not 'memory_limit' in self.config.keys():
			util.exit_with_error('Memory limit was not defined in config.yml.')
		if not 'scores' in self.config.keys():
			util.exit_with_error('Scores were not defined in config.yml.')

		self.compilers, self.timetool_path = self.validate_arguments(args)

		title = self.config["title"]
		print("Task %s (%s)" % (title, self.ID))
		config_time_limit = self.config["time_limit"]
		config_memory_limit = self.config["memory_limit"]
		self.time_limit = args.tl * 1000.0 if args.tl is not None else config_time_limit
		self.memory_limit = args.ml * 1024 if args.ml is not None else config_memory_limit
		self.cpus = args.cpus or mp.cpu_count()
		if self.time_limit == config_time_limit:
			print("Time limit (in ms):", self.time_limit)
		else:
			print("Time limit (in ms):", self.time_limit,
				util.warning(("[originally was %.1f ms]" % config_time_limit)))
		if self.memory_limit == config_memory_limit:
			print("Memory limit (in kb):", self.memory_limit)
		else:
			print("Memory limit (in kb):", self.memory_limit,
				util.warning(("[originally was %.1f kb]" % config_memory_limit)))
		self.scores = collections.defaultdict(int)
		print("Scores:")
		total_score = 0
		for group in self.config["scores"]:
			self.scores[group] = self.config["scores"][group]
			print("%2d: %3d" % (group, self.scores[group]))
			total_score += self.scores[group]
		if total_score != 100:
			print(util.warning("WARN: Scores sum up to %d (instead of 100)." % total_score))
		print()

		self.tests = self.get_tests(args.tests)
		self.groups = list(sorted(set([self.get_group(test) for test in self.tests])))
		self.possible_score = self.get_possible_score(self.groups)

		solutions = self.get_solutions(self.args.solutions)
		results = self.compile_and_run(solutions)
		validation_results = self.validate_expected_scores(results)
		self.print_expected_scores_diff(validation_results)
