from os import getcwd
from collections import namedtuple
from distutils.cmd import Command
from setuptools import setup
from yyagl.build.build import files
from yyagl.build.src import bld_src
from yyagl.build.devinfo import bld_devinfo
from yyagl.build.docs import bld_docs
from yyagl.build.pdf import bld_pdfs
from yyagl.build.uml import bld_uml


class AbsCmd(Command):

    env = {'APPNAME': 'yracing'}
    user_options = [('cores', None, '#cores')]

    def initialize_options(self): self.cores = 0

    def finalize_options(self): AbsCmd.env['CORES'] = self.cores


class SourcePkgCmd(AbsCmd):

    def run(self): bld_src(None, None, AbsCmd.env)


class DevInfoCmd(AbsCmd):

    def run(self):
        def cond_yyagl(src):
            thirdparty = str(src).startswith('yyagl/thirdparty/')
            venv = str(src).startswith('venv/')
            racing = str(src).startswith('yyagl/racing/')
            return thirdparty or venv or racing or \
                str(src).startswith('yyagl/tests')
        dev_conf = {'devinfo_yyagl': cond_yyagl}
        AbsCmd.env['DEV_CONF'] = dev_conf
        bld_devinfo(None, files(['py']), AbsCmd.env)


class DocsCmd(AbsCmd):

    def run(self):
        AbsCmd.env['DOCS_PATH'] = getcwd() + '/..'
        bld_docs(None, None, AbsCmd.env)


class PDFCmd(AbsCmd):

    def run(self):
        PDFInfo = namedtuple('PDFInfo', 'lng root fil excl')
        racing_fil = ['./game/*', './car/*',
                      './race/*', './track/*']
        racing_lst = [PDFInfo('python', '.', '*.py', racing_fil)]
        binfo_lst = [
            ('python', '*.py *.pdef'), ('lua', 'config.lua'),
            ('', '*.rst *.css_t *.conf'), ('html', '*.html'),
            ('javascript', '*.js')]
        #build_lst = [PDFInfo(binfo[0], 'build', binfo[1], [])
        #             for binfo in binfo_lst]
        pdf_conf = {
            'yracing': racing_lst,
            'yracing_car': [PDFInfo('python', './car', '*.py', [])],
            'yracing_race': [PDFInfo('python', './race', '*.py', [])],
            'yracing_track': [PDFInfo('python', './track', '*.py', [])]}
        AbsCmd.env['PDF_CONF'] = pdf_conf
        bld_pdfs(None, None, AbsCmd.env)


class UMLCmd(AbsCmd):

    def run(self):
        AbsCmd.env['UML_FILTER'] = []
        bld_uml(None, None, AbsCmd.env)


if __name__ == '__main__':
    setup(
        cmdclass={
            'source_pkg': SourcePkgCmd,
            'devinfo': DevInfoCmd,
            'docs': DocsCmd,
            'pdf': PDFCmd,
            'uml': UMLCmd},
        name='Yracing',
        version=0.12)
