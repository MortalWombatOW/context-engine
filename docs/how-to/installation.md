# How to Install ContextEngine

ContextEngine can be installed from source or set up for development.

## method 1: Install from Source

To install the package directly into your environment:

```bash
pip install git+https://github.com/MortalWombatOW/context-engine.git
```

## Method 2: Development Setup

If you want to modify ContextEngine itself:

1.  Clone the repository:
    ```bash
    git clone https://github.com/MortalWombatOW/context-engine.git
    cd context-engine
    ```

2.  Install in editable mode with development dependencies:
    ```bash
    pip install -e ".[dev]"
    ```

3.  Verify installation by running tests:
    ```bash
    pytest -v
    ```
