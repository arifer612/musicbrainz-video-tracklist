from sphinx_pyproject import SphinxConfig

config = SphinxConfig("../../pyproject.toml", globalns=globals(), style="poetry")
documentation_summary = config.description

# -- General configuration ---------------------------------------------------

extensions = config["extensions"]
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
}
