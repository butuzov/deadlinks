# Azure Pipelines

Azure Pipelines are part of Azure DevOps tool, and quite flexible CI platform.  It's quite complex and powerful, therefor we providing just a simple example specs in one job to check generated documentation.

<h3>Simple Azure Pipeline Process Example</h3>

```yaml
jobs:
- job: 'Builds'
  pool:
    vmImage: 'Ubuntu-16.04'

  steps:

    - checkout: self
      fetchDepth: 1
      displayName: "Repository Checkout"

    - task: UsePythonVersion@0
      inputs:
        versionSpec: '3.8'
        architecture: 'x64'
      displayName: "Setup Environment"

    - script: |
        python -m pip install --upgrade pip
        pip install https://github.com/butuzov/deadlinks/archive/develop.zip
        pip install -r requirements-docs.txt
      displayName: "deadlinks, mkdocs and theme"
      continueOnError: false

    - script: |
        mkdocs serve -q &
        deadlinks http://127.0.0.1:8000 -n10 -r3 --fiff --no-progress --no-colors
        kill -9 $!
      displayName: "checking external service"
      continueOnError: false

    - script: |
        mkdocs build -d site
        deadlinks internal --root=site -n10 -r3 --fiff --no-progress --no-colors
      displayName: "checking static files"
      continueOnError: false
```

<h4 id="additional-resources">Additional Resources</h4>

* &nbsp; [Azure Pipelines documentation](https://docs.microsoft.com/en-us/azure/devops/pipelines/?view=azure-devops)
