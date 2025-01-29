import os
import glob
import argparse
import subprocess

from sinol_make import util
from sinol_make.helpers import package_util, paths
from sinol_make.interfaces.BaseCommand import BaseCommand


class Command(BaseCommand):
    """
    Class for `doc` command.
    """
    LOG_PATTERNS = ['*~', '*.aux', '*.log', '*.dvi', '*.err', '*.inf', '*.out']

    def get_name(self):
        return "doc"

    def get_short_name(self):
        return "d"

    def compile_file_latex_div(self, file_path):
        print(f'Compiling {os.path.basename(file_path)} (latex to dvi)...')
        os.chdir(os.path.dirname(file_path))
        subprocess.run(['latex', file_path])
        dvi_file = os.path.splitext(file_path)[0] + '.dvi'
        dvi_file_path = os.path.join(os.path.dirname(file_path), dvi_file)
        if not os.path.exists(dvi_file_path):
            print(util.error('Compilation failed.'))
            return False

        process = subprocess.run(['dvipdf', dvi_file_path])
        if process.returncode != 0:
            print(util.error('Compilation failed.'))
            return False
        print(util.info(f'Compilation successful for file {os.path.basename(file_path)}.'))
        return True

    def compile_pdf_latex(self, file_path, compiler='pdflatex'):
        print(f'Compiling {os.path.basename(file_path)} ({compiler})...')
        os.chdir(os.path.dirname(file_path))
        for _ in range(3):
            subprocess.run([compiler, file_path])
        pdf_file = os.path.splitext(file_path)[0] + '.pdf'
        pdf_file_path = os.path.join(os.path.dirname(file_path), pdf_file)
        if not os.path.exists(pdf_file_path):
            print(util.error('Compilation failed.'))
            return False
        return True

    def make_file(self, file_path):
        """
        Compile the file two times to get the references right.
        """
        if self.compilation_method in ('pdflatex', 'lualatex'):
            return self.compile_pdf_latex(file_path, self.compilation_method)
        else:
            if not self.compile_file_latex_div(file_path):
                return False
            return self.compile_file_latex_div(file_path)

    def move_logs(self):
        output_dir = paths.get_cache_path('doc_logs')
        for pattern in self.LOG_PATTERNS:
            for file in glob.glob(os.path.join(os.getcwd(), 'doc', pattern)):
                os.rename(file, os.path.join(output_dir, os.path.basename(file)))
        print(f'Compilation log files can be found in {os.path.relpath(output_dir, os.getcwd())}')

    def configure_subparser(self, subparser: argparse.ArgumentParser):
        parser = subparser.add_parser(
            self.get_name(),
            help='Compile latex files to pdf',
            description='Compiles latex files to pdf. By default compiles all files in the `doc` directory.\n'
                        'You can also specify files to compile.')
        parser.add_argument('--latex-compiler', dest='latex_compiler', choices=['auto', 'pdflatex', 'latex_dvi', 'lualatex'],
                            help='Compiler used to compile documents. Available options:\n'
                                 ' auto - uses the compiler based on the image types (default option, if not configured in config.yml).\n'
                                 ' pdflatex - uses pdflatex. Works with .png and .jpg images.\n'
                                 ' lualatex - uses lualatex. Like pdflatex, but supports the graph drawing library of TikZ.\n'
                                 ' latex_dvi - uses latex and dvipdf. Works with .ps and .eps images.', default=argparse.SUPPRESS)
        parser.add_argument('files', type=str, nargs='*', help='files to compile')
        return parser

    def run(self, args: argparse.Namespace):
        args = util.init_package_command(args)

        # Note: when other commands call DocCommand as a subroutine, they provide
        # their own argparse.Namespace instead of going through the argparse
        # configuration in configure_subparser. To match their behavior,
        # we configure argparse to omit the latex_compiler attribute entirely
        # when it is not provided by the user, instead of using the default
        # behavior of defaulting to None.
        if not hasattr(args, 'latex_compiler'):
            config = package_util.get_config()
            args.latex_compiler = config.get('sinol_latex_compiler', 'auto')

        if args.latex_compiler == 'pdflatex':
            self.compilation_method = 'pdflatex'
        elif args.latex_compiler == 'lualatex':
            self.compilation_method = 'lualatex'
        elif args.latex_compiler == 'latex_dvi':
            self.compilation_method = 'latex_dvi'
        elif args.latex_compiler == 'auto':
            self.compilation_method = 'pdflatex'
            for extension in ['ps', 'eps']:
                if glob.glob(os.path.join(os.getcwd(), 'doc', f'*.{extension}')) != []:
                    self.compilation_method = 'latex_dvi'
        else:
            util.exit_with_error("Unrecognized latex compiler")

        if args.files == []:
            self.files = glob.glob(os.path.join(os.getcwd(), 'doc', '*.tex'))
        else:
            self.files = []
            for file in args.files:
                if not os.path.exists(file):
                    print(util.warning(f'File {file} does not exist.'))
                else:
                    self.files.append(os.path.abspath(file))
        if self.files == []:
            print(util.warning('No files to compile.'))
            return

        original_cwd = os.getcwd()
        failed = []
        for file in self.files:
            if not self.make_file(file):
                failed.append(file)
        os.chdir(original_cwd)

        self.move_logs()
        if failed:
            for failed_file in failed:
                print(util.error(f'Failed to compile {failed_file}'))
            util.exit_with_error('Compilation failed.')
        else:
            print(util.info('Compilation was successful for all files.'))
