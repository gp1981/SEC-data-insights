from setuptools import setup, find_packages

setup(
    name="sec-data-insights",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "pandas>=2.1.0",
        "click>=8.1.7"
    ]
)