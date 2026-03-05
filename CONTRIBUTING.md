# Contributing to Tabular-Enhancement-Tool

First off, thank you for considering contributing to the Tabular-Enhancement-Tool! It's people like you who make this tool better for everyone.

## Code of Conduct

By participating in this project, you agree to abide by the same standards of professional and respectful behavior expected in any open-source community.

## How Can I Contribute?

### Reporting Bugs

- **Check the FAQ**: Before reporting a bug, please check the [FAQ](https://tabular-enhancement-tool.readthedocs.io/en/latest/faq.html) to see if it's already covered.
- **Use the Issue Tracker**: Report bugs via the GitHub Issue Tracker.
- **Be Detailed**: Include your Python version, operating system, and a minimal reproducible example (code and sample data).

### Suggesting Enhancements

- **Open an Issue**: Describe the enhancement you'd like to see and why it would be useful.
- **Discuss**: Engage with the maintainers to refine the idea.

### Pull Requests

1.  **Fork the Repository**: Create your own fork of the project.
2.  **Create a Branch**: Use a descriptive branch name (e.g., `fix/api-timeout-error` or `feat/new-auth-method`).
3.  **Implement Changes**:
    - Follow the existing code style (Ruff is used for formatting).
    - Add tests for any new functionality or bug fixes.
    - Ensure all existing tests pass.
4.  **Run Linting**: Run `ruff check .` and `ruff format .` before committing.
5.  **Submit the PR**: Provide a clear description of what the PR does and link any relevant issues.

## Development Environment Setup

1.  Clone the repository:
    ```bash
    git clone https://github.com/Mikuana/tabular-enhancement-tool.git
    cd tabular-enhancement-tool
    ```
2.  Install the package in editable mode with test dependencies:
    ```bash
    pip install -e ".[test]"
    ```
3.  Run tests:
    ```bash
    pytest
    ```

## Coding Standards

- **Style**: We use [Ruff](https://github.com/astral-sh/ruff) for linting and formatting.
- **Tests**: We aim for high test coverage. Please use `pytest` for writing tests.
- **Documentation**: We use Sphinx for documentation. Update `.rst` files in the `docs/` directory if you change the API or add features.

## License

By contributing, you agree that your contributions will be licensed under the project's [MIT License](./LICENSE).
