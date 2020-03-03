# GitHub Actions

If you using Github environment, you probably can be interested in running checks right in your pipeline. Here is a simple example of deploying sphinx based documentation to github pages with a `deadlinks` check step.

<h3>Simple CI Pipeline Process</h3>

```yaml
name: Build, Test and Deploy Documentation

on: [push]

jobs:

  build:

    runs-on: ubuntu-latest

    strategy:
      matrix:
        python-version: [ 3.7 ]

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v1
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install Dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Build html artifacts
      run: |
        sphinx-build docs html -qW --keep-going;

    - name: deadlinks checker
      run: |
        pip install deadlinks
        deadlinks internal -n10 --root=html --no-progress --fiff

    - name: Deploy To Github Pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./html
        publish_branch: gh-pages
```

<h3>Using docker image</h3>

If your source action doesn't contain python and can't install `deadlinks` as package, you always can use docker image (github actions supported since version 0.3.0)

Replace previous `deadlinks checker` step with next one.

```yaml

    - name: deadlinks checker
      uses: docker://docker.io/butuzov/deadlinks:latest
      with:
        args: internal -n10 --root=html --no-progress --fiff
```
