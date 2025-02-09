import os
from pathlib import Path
from sphinx.application import Sphinx
from sphinx.util.docutils import docutils_namespace

class_reprs:set = set()
each_class_obj_attrs = {}


def get_sphinx_app(src_dir, conf_dir, out_dir, doctree_dir):
    app = Sphinx(
        srcdir=src_dir,
        confdir=conf_dir,
        outdir=out_dir,
        doctreedir=doctree_dir,
        buildername='html',
    )
    return app
def parse_rst_folder_with_sphinx(folder_path):

    src_dir = folder_path
    conf_dir = folder_path  # Assuming conf.py is in the root of the folder
    print('conf_dir:', conf_dir, Path(conf_dir).exists())
    out_dir = os.path.join(folder_path, '_build')
    doctree_dir = os.path.join(folder_path, '_doctrees')

    app = get_sphinx_app(src_dir, conf_dir, out_dir, doctree_dir)
    with docutils_namespace():
        app.build(force_all=True)
    return app.env

def build_document_structure(env):
    document_structure = {}
    def build_structure(docname, parent):
        if docname not in env.toctree_includes:
            return
        parent[docname] = {}
        for child in env.toctree_includes[docname]:
            build_structure(child, parent[docname])
    
    root_doc = env.config.master_doc
    build_structure(root_doc, document_structure)
    return document_structure



        
