# Static Site Generators

There are [number of options](https://www.staticgen.com/) you can use for static website or documentation generation, and we honestly can't recommend any particular. However it's important to understand that `deadlinks` itself designated to eliminate just one issue with documentation - dead or broken links, static site generator you using, can have additional features that will improve your CI process. It's nice to know `what` tools can do `what` and integrate their features into CI.

Static site generator can:
* Show information about missing links or not included files.
* Describe markup errors found in source files
* Check for the issues with external or internal links too.

This is incomplete list of known CI features you can integrate in your pipeline.


## [Sphinx](https://www.sphinx-doc.org/)

Sphinx itself, doesn't support files serving, so we will always rebuild files before testing, however it checks included, missing links, and generate corresponding warnings. You also can use `sphinx` via `setup.py`

```bash
#  -q will limit output only to warnings
#  -W will turn warnings into errors
#  --keep-going will show all found errors, not just first one.
sphinx-build docs html -qW --keep-going

# same effect if used via setup.py
python3 setup.py build_sphinx -c docs --build-dir build -qW --keep-going
```

## [MkDocs](https://www.mkdocs.org/)

MkDocs is quite nice and configurable static docs generator, which can serve files and exit on warnings (`--strict` option).

```bash
# Serve files at 127.0.0.1:8080
mkdocs serve --strict --dirtyreload --dev-addr 127.0.0.1:8080

# Just build files
mkdocs build --strict
```
