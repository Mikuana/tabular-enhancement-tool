from setuptools import setup, find_packages

setup(
    name="Tabular-Enhancement-Tool",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "requests",
        "openpyxl",
    ],
    extras_require={
        "test": ["pytest", "coverage"],
    },
    entry_points={
        "console_scripts": [
            "tabular-enhancer=tabular_enhancement_tool.cli:main",
        ],
    },
    author="Junie",
    description="A Python package for asynchronously enhancing tabular files via APIs",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.6",
)
