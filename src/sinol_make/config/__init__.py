import yaml, os, subprocess

class Config:
	def __init__(self):
		config_path = os.path.join(os.path.dirname(__file__), 'config.yml')
		if not os.path.exists(config_path):
			open(config_path, 'w').write(yaml.dump({}))
			self.setup()

	def setup(self):
		print("Configure your compilers:")
		
		self.set('c_compiler', self.__ask_value("C compiler", "gcc"))
		self.set('cpp_compiler', self.__ask_value("C++ compiler", "g++"))
		self.set('python_compiler', self.__ask_value("Python compiler", "python3"))
		self.set('java_compiler', self.__ask_value("Java compiler", "javac"))

	def set(self, key, value):
		config_path = os.path.join(os.path.dirname(__file__), 'config.yml')
		config = yaml.load(open(config_path, 'r'))
		config[key] = value
		open(config_path, 'w').write(yaml.dump(config))

	def get(self, key):
		config_path = os.path.join(os.path.dirname(__file__), 'config.yml')
		config = yaml.load(open(config_path, 'r'))
		return config[key]

	def __ask_value(self, prompt, default):
		valid = False
		while not valid:
			value = input(prompt + " (" + default + "): ") or default
			
			if subprocess.call([value, "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
				valid = True
			else:
				print("Invalid compiler")

		return value