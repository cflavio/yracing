import sys, os.path, os
sys.path += [os.path.abspath(os.path.join(os.getcwd(), os.pardir)) + '/yyagl']
from collections import namedtuple
from build.build import extensions, files, img_tgt_names, \
    set_path, src_fpath, devinfo_fpath, docs_fpath, pdf_fpath, test_fpath
from build.src import bld_src
from build.devinfo import bld_devinfo
from build.test import bld_ut
from build.docs import bld_docs
from build.imgs import bld_images
from build.pdf import bld_pdfs
from build.uml import bld_uml


SCONS_ENABLE_VIRTUALENV=1
argument_info = [  # (argname, default value)
    ('path', 'built'), ('source', 0), ('devinfo', 0),
    ('docs', 0), ('pdf', 0), ('cores', 0), ('uml', 0)]
args = {arg: ARGUMENTS.get(arg, default) for (arg, default) in argument_info}
path = set_path(args['path'])
app_name = 'yracing'

pargs = {'dst_dir': path, 'appname': app_name}
src_path = src_fpath.format(**pargs)
devinfo_path = devinfo_fpath.format(**pargs)
tests_path = test_fpath.format(**pargs)
docs_path = docs_fpath.format(**pargs)
pdf_path = pdf_fpath.format(**pargs)

bld_src = Builder(action=bld_src)
bld_devinfo = Builder(action=bld_devinfo)
bld_docs = Builder(action=bld_docs)
bld_pdfs = Builder(action=bld_pdfs)
bld_uml = Builder(action=bld_uml)

env = Environment(BUILDERS={
    'source': bld_src, 'devinfo': bld_devinfo,
    'docs': bld_docs, 'pdf': bld_pdfs, 'uml': bld_uml})
env['APPNAME'] = app_name
env['CORES'] = int(args['cores'])
PDFInfo = namedtuple('PDFInfo', 'lng root fil excl')
racing_fil = ['./game/*', './car/*',
              './race/*', './track/*']
racing_lst = [PDFInfo('python', '.', '*.py', racing_fil)]
binfo_lst = [
    ('python', '*.py *.pdef'), ('lua', 'config.lua'),
    ('', '*.rst *.css_t *.conf'), ('html', '*.html'), ('javascript', '*.js')]
build_lst = [PDFInfo(binfo[0], 'build', binfo[1], [])
             for binfo in binfo_lst]
pdf_conf = {
    'yracing': racing_lst,
    'yracing_car': [PDFInfo('python', './car', '*.py', [])],
    'yracing_race': [PDFInfo('python', './race', '*.py', [])],
    'yracing_track': [PDFInfo('python', './track', '*.py', [])]}
env['PDF_CONF'] = pdf_conf

cond_racing = lambda s: not str(s).startswith('yyagl/racing/')
def cond_yyagl(src):
    #not_yyagl = not str(src).startswith('yyagl/')
    thirdparty = str(src).startswith('yyagl/thirdparty/')
    venv = str(src).startswith('venv/')
    racing = str(src).startswith('yyagl/racing/')
    return thirdparty or venv or racing or \
        str(src).startswith('yyagl/tests')
dev_conf = {'devinfo_yyagl': cond_yyagl}
env['DEV_CONF'] = dev_conf

VariantDir(path, '.')

general_src = files(extensions, ['built'])
if args['source']:
    env.source([src_path], general_src)
if args['devinfo']:
    env.devinfo([devinfo_path], files(['py'], ['venv', 'thirdparty']))
if args['docs']:
    env.docs([docs_path], files(['py'], ['venv', 'thirdparty']))
if args['pdf']:
    env.pdf([pdf_path], files(['py'], ['venv', 'thirdparty']))
if args['uml']:
    env.uml(
        ['built/uml_classes.pdf'],
        general_src)