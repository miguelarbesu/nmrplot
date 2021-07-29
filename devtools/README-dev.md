# Information for developers

If you want to do a developer install, start by installing this package as

```
pip install -e .
```

This will make your local copy of nmrplot available. 
You can then modify or extend the program and directly test it.

## Best practices and implementation

This project enforces [best practices](https://molssi.org/education/best-practices/) in
(scientific) software development that help producing open, reproducible and reliable
research tools. Here is an overview and the specific implementation. 

### Version control

The foundation of all best practices is version control. [`git`](https://git-scm.com/)
is the tool of choice in this project. [GitHub](https://github.com/) is the platform of
choice used to host git repositories online. [GitHub
actions](https://github.com/features/actions) are used to automatize the use of some
tools (see below)

### Testing

Pytest is the library of choice. You can run all tests locally with

```
pytest
```

### Code formatting / linting

[`flake8`](https://flake8.pycqa.org/) and [`black`](https://black.readthedocs.io/en/stable/) are used to enforce style rules. `isort` helps sorting the imports nicely.

All these tools are handled as [`pre-commit`](https://pre-commit.com/) hooks. These are installed upon CONTINUE

### Continuous Integration (CI)

[This GitHub Action](../.github/workflows/CI.yaml) automatically runs Pytest on Python
3.6, 3.7, 3.8 and 3.9 on Linux, Mac and Windows instances on push/pull requests to the
GitHub upstream.

CONTINUE

### Documentation

#### Mkdocs

#### Docstrings

Google-style

## Recommended working set up

An [IDE](https://en.wikipedia.org/wiki/Integrated_development_environment) is a handy way of automatizing processes. I reccomend [VS code](https://code.visualstudio.com/).

## Optional setup for devs

### Adding the project to your GitHub account

To add this repository to your GitHub account, please run[*]
   
```bash
devtools/setup-github.sh
```

[*]: *Requires the [GitHub CLI](https://github.com/cli/cli))*


<!-- - Create a dedicated virtual environment 

```
devtools/setup-venv.sh
``` -->
 