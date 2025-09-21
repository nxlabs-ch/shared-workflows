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

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    "papersize": "a4paper",
    "preamble": r"""
        \makeatletter
        \fancypagestyle{normal}{
            \fancyhead[RO]{{\py@HeaderFamily\nouppercase{\rightmark}}}
            \fancyhead[LE]{{\py@HeaderFamily\nouppercase{\leftmark}}}
            \fancyfoot[LO, RE]{{\scriptsize (c) 2025 Copyright NxLabs, all rights reserved.}}
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
    """Setup function for custom LaTeX task list handling."""
    from sphinx.writers.latex import LaTeXTranslator

    # Store the original methods
    original_visit_bullet_list = LaTeXTranslator.visit_bullet_list
    original_depart_bullet_list = LaTeXTranslator.depart_bullet_list
    original_visit_list_item = LaTeXTranslator.visit_list_item
    original_depart_list_item = LaTeXTranslator.depart_list_item

    def visit_bullet_list_custom(self, node):
        # Check if this is a task list
        if "contains-task-list" in node.get("classes", []):
            self.body.append("\\begin{itemize}\n")
            self.context.append("\\end{itemize}\n")
        else:
            # Use original behavior for regular bullet lists
            original_visit_bullet_list(self, node)

    def depart_bullet_list_custom(self, node):
        if "contains-task-list" in node.get("classes", []):
            self.body.append(self.context.pop())
        else:
            original_depart_bullet_list(self, node)

    def visit_list_item_custom(self, node):
        # Check if this is a task list item
        if "task-list-item" in node.get("classes", []):
            # Look for a raw HTML element containing the checkbox
            is_checked = False

            # Search through all descendants for a raw element
            for child in node.traverse():
                if hasattr(child, 'tagname') and child.tagname == 'raw':
                    if child.get('format') == 'html':
                        # Parse the raw HTML content to look for checkbox
                        raw_content = str(child.astext())
                        if 'type="checkbox"' in raw_content:
                            # Check if the checkbox is checked
                            is_checked = 'checked="checked"' in raw_content
                            break

            # Render the appropriate checkbox
            if is_checked:
                self.body.append("\\item[\\checkedbox] ")
            else:
                self.body.append("\\item[\\emptybox] ")
        else:
            # Use original behavior for regular list items
            original_visit_list_item(self, node)

    def depart_list_item_custom(self, node):
        if "task-list-item" in node.get("classes", []):
            self.body.append("\n")
        else:
            original_depart_list_item(self, node)

    # Override the methods
    LaTeXTranslator.visit_bullet_list = visit_bullet_list_custom
    LaTeXTranslator.depart_bullet_list = depart_bullet_list_custom
    LaTeXTranslator.visit_list_item = visit_list_item_custom
    LaTeXTranslator.depart_list_item = depart_list_item_custom

    return {
        "version": "1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
