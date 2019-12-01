# Travis CI

Example integration can take next steps and looks like code below:

<h3>Handling Static Files</h3>

If tool, you using for static site generation doesn't support serving files, you can pass this task to deadlinks using `internal` keyword and `--root` option.

```yaml

language: python
python: 3.8

# Install step will install dependencies (sphinx) and deadlinks
install:
- pip install -r requirements.txt
- pip install deadlinks

# Build step will create artifacts (in html directory) and deadlinks
# will check directory  `html` and fail if failed urls found.
script:
- sphinx-build docs html -qW --keep-going
- deadlinks internal -R html --no-progress --no-colors --fiff

# You can deploy artifacts to github pages if pipeline passes.
deploy:
  provider: pages
  skip_cleanup: true
  github_token: $GITHUB_TOKEN
  local_dir: html
  on:
    branch: master
```

Read more about `sphinx` at [Static Site Generators](../static-site-generators#sphinx) page.

<h3>Serving Files</h3>

If your tool can serve html files, just run serving in background

```yaml
language: python
python: 3.8

# Install step will install dependencies (mkdocs) and deadlinks
install:
- pip install -r requirements.txt
- pip install deadlinks

# We running build for static files first, and then running it again in the `serve`
# mode, `deadlinks` is checking web address on which documentation served.
script:
- mkdocs build --strict
- mkdocs serve --dirtyreload --dev-addr 127.0.0.1:8080 &
- deadlinks http://127.0.0.1:8080 -n10 -r3  --no-progress --no-colors --fiff

```

Read more about `mkdocs` at [Static Site Generators](../static-site-generators#mkdocs) page.
