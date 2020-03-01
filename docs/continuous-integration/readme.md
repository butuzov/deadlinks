
# Continuous Integration

You can automate deadlinks checks using any of the modern `Continues Integration` tools. Use tutorials and templates we created for  popular CIs.

<h2>Introduction</h2>
CI procecess for out tool can be described in 2/3 sentances.

1. Documentation tools compiling documentation.
2. Buildin/Standalone server serving documentation (as background process).
3. `deadlinks` checks whats there and generate report.

If tool you using to create documentation has support for links checking, please implement this step alongside deadlinks into your pipeline.



<h2>Continues Integration Providers</h2>

* [Azure Pipelines](azure-pipelines.md)
* [CircleCI](circleci.md)
* [GitHub Actions](github-actions.md)
* [tox](tox.md)
* [Travis CI](travis-ci.md)
