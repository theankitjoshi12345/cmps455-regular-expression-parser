"""Compatibility entry point for older pip versions."""

from setuptools import find_packages, setup


setup(
    name="cmps455-regular-expression-parser",
    version="0.1.0",
    description="CMPS455 regular-expression scanner and recursive-descent recognizer",
    package_dir={"": "src"},
    packages=find_packages("src"),
    python_requires=">=3.9",
)
