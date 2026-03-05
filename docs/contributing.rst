Contributing
============

Welcome! We're glad you're interested in contributing to the **Tabular-Enhancement-Tool**.

Whether you're fixing a bug, suggesting a new feature, or improving the documentation, your help is appreciated.

How to Contribute
-----------------

1. **Fork the Repository**: Start by forking the project to your own GitHub account.
2. **Clone the Project**: Clone your fork to your local machine.
3. **Create a Branch**: Create a new branch for your changes (e.g., ``git checkout -b feature/awesome-new-feature``).
4. **Make Your Changes**: Implement your changes, following the existing code style and adding tests where applicable.
5. **Run Tests**: Ensure all existing and new tests pass using ``pytest``.
6. **Commit Your Changes**: Commit your changes with a clear and descriptive message.
7. **Push and Open a Pull Request**: Push your branch to your fork and submit a PR to the main repository.

Development Environment Setup
-----------------------------

To set up a local development environment:

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/Mikuana/tabular-enhancement-tool.git
   cd tabular-enhancement-tool

   # Create a virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install development dependencies
   pip install -e .[test]
   pip install -r requirements-docs.txt

Running Tests
-------------

We use ``pytest`` for testing. Run the following command from the project root:

.. code-block:: bash

   pytest

Code Style
----------

We use **Ruff** for linting and formatting. Please ensure your code adheres to the project's standards by running:

.. code-block:: bash

   ruff check .
   ruff format .

Documentation
-------------

If you're modifying documentation, you can build it locally to preview your changes:

.. code-block:: bash

   cd docs
   make html  # On Windows: .\make.bat html

The built documentation will be available in ``docs/_build/html/index.html``.
