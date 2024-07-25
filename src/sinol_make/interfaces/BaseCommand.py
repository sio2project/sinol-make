class BaseCommand:
    """
    Base class for command
    """


    def get_name(self):
        """
        Get name of command
        """
        pass


    def get_short_name(self):
        """
        Get short name of command
        """
        return None


    def configure_subparser(self, subparser):
        """
        Configure subparser for command
        """
        pass


    def run(self, args):
        """
        Run command
        """
        pass
