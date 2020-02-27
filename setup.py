from distutils.cmd import Command
from setuptools import setup
from yyagl.build.build import files
from yyagl.build.src import bld_src
from yyagl.build.devinfo import bld_devinfo


class AbsCmd(Command):

    env = {'APPNAME': 'yracing'}
    user_options = []

    def initialize_options(self): pass

    def finalize_options(self): pass


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


if __name__ == '__main__':
    setup(
        cmdclass={
            'source_pkg': SourcePkgCmd,
            'devinfo': DevInfoCmd},
        name='Yracing',
        version=0.12)
