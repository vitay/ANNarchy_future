# Documentation for ANNarchy

The documentation is done using mkdocs and the material theme.

Required packages:

```bash
pip install mkdocs mkdocs-material mkdocstrings pymdown-extensions
```

In the root directory (where mkdocs.yml lies), preview the doc with:

```bash
mkdocs serve
```

To generate the static website in `site/`:

```bash
mkdocs build
```

To deploy on Github pages:

```bash
mkdocs gh-deploy
```

Note that docstrings should use Google's style:

<https://mkdocstrings.github.io/handlers/python/#google-style>