class BaseCommand:
	"""
	Base class for command
	"""


	def get_name(self):
		"""
		Get name of command
		"""


	def configure_subparser(self, subparser):
		"""
		Configure subparser for command
		"""


	def run(self, args):
		"""
		Run command
		"""
