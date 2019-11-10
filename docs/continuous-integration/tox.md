# Tox

[Tox](https://tox.readthedocs.io/en/latest/) is a test automation tool designed to work with python projects. If you using it within your continues integration or continues deployment pipeline it makes sense to implement links checking within tox.

Next example is:

1.  Building documentation using [`mkdocs`](https://www.mkdocs.org/) and `-s` options will abort pipeline with an error if a problem with `mkdocs` itself or documentation found.
2.  Run `mkdocs` with `serve` command in the background to make it available at 127.0.0.1:3001
3.  Run deadlinks against http://127.0.0.1:3001/ in 10 threads and retry  3 times to get URLs, with no progress report and *fail* if failed URLs are found.
4.  Failed URLs will be printed to `stdout`.
5.  `deadlinks` (version 0.1.0 and above) installed from requirements_dev.txt.


```ini
[testenv:docs]
basepython = python3
ignore_errors = False
whitelist_externals = sh
commands =
    ; -s abort the build on any warnings
    mkdocs build -s --clean --site-dir build/docs/html --theme readthedocs
    ; running mkdocs to serve the documentation at 127.0.0.1:3001
    sh -c 'mkdocs serve --dev-addr 0.0.0.0:3001 --theme readthedocs 2>&1 > /dev/null &'
    ; checking links liveness
    deadlinks http://127.0.0.1:3001/ -n 10 -r 3 --no-progress --fiff

deps =
     -r{toxinidir}/requirements_dev.txt
```
