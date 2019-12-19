# CircleCI

CircleCI is reliable CI/CD service which can run your loads, it has nice UI^ and you can create nice pipelines there. In order to run you CI load on CircleCI create file `.circleci/config.yaml` in your repository and follow ("register") project on [CircleCI.com](https://circleci.com/). You also can setup `circleci` on github side of your project (as "bot").

<h3>Simple CI Pipeline Process</h3>

```yaml
version: 2
jobs:
  build:
    working_directory: ~/repo

    docker:
      - image: circleci/python:3.7

    steps:
      - checkout

      - run:
          name: install deadlinks, mkdocs and theme
          command: |
            sudo python3 -m pip install deadlinks
            sudo python3 -m pip install -r requirements-docs.txt

      - run:
          name: checking external service (files served by mkdocs)
          command: |
            mkdocs serve -q &
            deadlinks http://127.0.0.1:8000 -n10 -r3 --fiff --no-progress --no-colors

      - run:
          name: checking static files
          command: |
            mkdocs build -d site
            deadlinks internal --root=site -n10 -r3 --fiff --no-progress --no-colors
```

<h3>Deployment Example</h3>

This is more complex CI/CD Process, that covers multiple stages and github deployment. You also can read additional resources[`*`](#additional-resources) regarding GitHub Pages and CircleCI deployments.

```yaml
defaults: &defaults
  docker:
    - image: circleci/python:3.8
  working_directory: ~/repo


version: 2
jobs:

  # Tests & builds & more tests
  tests-n-builds:
    docker:
    - image: circleci/python:3.8
    working_directory: ~/repo
    steps:
    - checkout
    - run:
        name: "Python: install requirements"
        command: |
          sudo python3 -m pip install deadlinks
          sudo python3 -m pip install -r requirements-docs.txt

    - run:
        name: "Deadlinks: checking external (web) resource"
        command: |
          mkdocs serve -q &
          deadlinks http://127.0.0.1:8000 -n10 -r3 --fiff --no-progress --no-colors

    - run:
        name: "Building artifacts (Documentation)"
        command:  mkdocs build -d site

    - run:
        name: "Deadlinks: checking internal (files) resource"
        command: deadlinks internal -n10 -r3 --root=site --fiff --no-progress --no-colors

    - persist_to_workspace:
        root: site
        paths: .

  # Deploy to github pages.
  deploy:
    docker:
    - image: circleci/node:12.13
    working_directory: ~/repo

    steps:
    - checkout
    - run:
        name: Prepare branches locally
        command: |
          git checkout gh-pages
          git checkout master

    - run:
        name: Set up gh-pages in worktree for easy artifact copying
        command: |
          mkdir ../gh-pages
          git worktree add ../gh-pages gh-pages

    - attach_workspace:
        at: site

    - run:
        name: Disable jekyll builds
        command: touch site/.nojekyll

    - add_ssh_keys:
        fingerprints:
          - "cd:4e:ff:73:71:a1:86:fa:cc:5d:0f:eb:dc:f5:db:88"

    - run:
        name: "GitHub Pages deployment"
        command: |
          rm -r ../gh-pages/*
          cp -r site/* ../gh-pages
          cd ../gh-pages
          ls -la
          git config --global user.email "ci@deployments.net"
          git config --global user.name  "CircleCI"
          git add .
          git commit --allow-empty -m "Build triggered by CircleCI"
          git push -u origin gh-pages


workflows:
  version: 2
  test-build-and-deploy:
    jobs:
    - tests-n-builds:
        filters:
          branches: { ignore: "gh-pages" }

    - deploy:
        requires:
        - tests-n-builds
        filters:
          branches: { only: "master" }
```


<h4 id="additional-resources">Additional Resources</h4>

  * &nbsp;[CircleCI Documentation](https://circleci.com/docs/)
  * &nbsp;[CircleCI Blog: Tutorials](https://circleci.com/blog/tag/tutorials/)
  * &nbsp;[Deploying documentation to GitHub Pages with continuous integration](https://circleci.com/blog/deploying-documentation-to-github-pages-with-continuous-integration/)
  * &nbsp;[How to Deploy to Github Pages Using CircleCI 2.0 + Custom Jekyll Dependencies](https://jasonthai.me/blog/2019/07/22/how-to-deploy-a-github-page-using-circleci-20-custom-jekyll-gems/)
