# MarkItDown

> [!TIP]
> MarkItDown is a Python package and command-line utility for converting various files to Markdown (e.g., for indexing, text analysis, etc).
>
> For more information, and full documentation, see the project [README.md](https://github.com/syedarifulislamemon2010/_markitdown_) on GitHub.

> [!IMPORTANT]
> MarkItDown performs I/O with the privileges of the current process. Like open() or requests.get(), it will access resources that the process itself can access. Sanitize your inputs in untrusted environments, and call the narrowest `convert_*` function needed for your use case (e.g., `convert_stream()`, or `convert_local()`). See the [Security Considerations](https://github.com/syedarifulislamemon2010/_markitdown_#security-considerations) section of the documentation for more information.

## Installation

From PyPI:

```bash
pip install 'markitdown[all]'
```

From source:

```bash
git clone https://github.com/syedarifulislamemon2010/_markitdown_.git
cd _markitdown_
pip install -e 'packages/markitdown[all]'
```

## Usage

### Command-Line

```bash
markitdown path-to-file.pdf > document.md
```

### Python API

```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("test.xlsx")
print(result.markdown)
```

### More Information

For more information, and full documentation, see the project [README.md](https://github.com/syedarifulislamemon2010/_markitdown_) on GitHub.

