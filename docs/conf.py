# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
from pathlib import Path
from datetime import date
# import sys
# sys.path.insert(0, os.path.abspath('.'))


def get_version():
    try:
        with open(
            Path(os.path.dirname(os.path.abspath(__file__)), "..", ".version"), "r"
        ) as file:
            return file.read().strip()
    except Exception:
        return os.environ.get('GIT_VERSION_NUMBER', 'development')


# -- Project information -----------------------------------------------------

project = 'Shared Workflows'
author = "Nx Labs"
copyright = f"{date.today().year}, {author}"

# The full version, including alpha/beta/rc tags
release = get_version()


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "myst_parser",
]

# MyST parser configuration
myst_enable_extensions = [
    "tasklist",  # Enable GitHub-style task lists
]


# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = 'alabaster'

# A dark/lite read-the-docs like theme
import sphinx_pdj_theme

html_theme = "sphinx_pdj_theme"
html_theme_path = [sphinx_pdj_theme.get_html_theme_path()]


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Add custom CSS with higher priority
html_css_files = [
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css",
    "custom.css",
]

# Add custom JavaScript files
# This fixes and issue with nested lists in MyST markdown files
html_js_files = [
    "fix-nested-lists.js",
]

# -- Options for LaTeX output ------------------------------------------------

# `latex_engine` is deliberately left at its pdflatex default: this repository builds
# its PDF both ways, through `uv-docs.yml` (pdflatex) and `tectonic-docs.yml` (XeTeX).
# The `latex` target in `uv-makefile` passes `-D latex_engine=xelatex` for the Tectonic
# build. Setting it here instead would break the pdflatex one, which has no XeTeX binary.
# A project using only `tectonic-docs.yml` should set `latex_engine = "xelatex"` here.

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    "papersize": "a4paper",
    # Sphinx >= 7.4 decorates admonition titles with icons from `fontawesome5`
    # whenever that package happens to be installed. Tectonic's bundle ships it
    # but not the `expl3` it depends on, which is a hard error; `none` disables
    # the icons and keeps the build independent of what TeX files are around.
    "sphinxsetup": "iconpackage=none",
    "preamble": r"""
        \makeatletter
        \fancypagestyle{normal}{
            \fancyhead[RO]{{\py@HeaderFamily\nouppercase{\rightmark}}}
            \fancyhead[LE]{{\py@HeaderFamily\nouppercase{\leftmark}}}
            \fancyfoot[LO, RE]{{\scriptsize (c) 2026 Copyright NxLabs, all rights reserved.}}
        }
        \makeatother
        
        % Task list checkbox support
        \usepackage{amssymb}
        
        % Define checkbox symbols
        \newcommand{\emptybox}{$\square$}
        \newcommand{\checkedbox}{$\blacksquare$}
    """,
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (
        "index",
        "shared-workflows.tex",
        "Shared Workflows' Documentation",
        {author},
        "manual",
    ),
]


def setup(app):
    r"""Render MyST task lists as LaTeX checkbox items.

    The `tasklist` extension emits checkboxes as raw HTML, which Sphinx's LaTeX
    writer discards (`visit_raw` only keeps nodes whose format is `latex`), and
    Sphinx has no task-list support of its own. Without this the checkboxes
    disappear from the PDFs, silently and without a build warning.

    So the list is re-created as an `itemize` whose item labels are the
    \emptybox / \checkedbox macros defined in `latex_elements["preamble"]`.
    """
    from docutils import nodes
    from sphinx.writers.latex import LaTeXTranslator

    def has_class(node, name):
        return name in node.get("classes", [])

    class TaskListLaTeXTranslator(LaTeXTranslator):
        def visit_bullet_list(self, node):
            # Unlike the base implementation this ignores `compact_list`, which
            # keeps the output identical to what this override produced before.
            if has_class(node, "contains-task-list"):
                self.body.append("\\begin{itemize}\n")
            else:
                super().visit_bullet_list(node)

        def depart_bullet_list(self, node):
            if has_class(node, "contains-task-list"):
                self.body.append("\\end{itemize}\n")
            else:
                super().depart_bullet_list(node)

        def visit_list_item(self, node):
            if not has_class(node, "task-list-item"):
                super().visit_list_item(node)
                return
            checked = False
            for raw in node.findall(nodes.raw):
                if raw.get("format") == "html" and 'type="checkbox"' in raw.astext():
                    checked = 'checked="checked"' in raw.astext()
                    break
            self.body.append(
                "\\item[\\checkedbox] " if checked else "\\item[\\emptybox] "
            )

        def depart_list_item(self, node):
            if has_class(node, "task-list-item"):
                self.body.append("\n")
            else:
                super().depart_list_item(node)

    app.set_translator("latex", TaskListLaTeXTranslator, override=True)

    return {
        "version": "1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
