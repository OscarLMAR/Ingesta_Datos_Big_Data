from setuptools import setup, find_packages


setup(
    name="ingesta-datos-big-data",
    version="1.0.0",
    description="Proyecto de ingesta de datos desde un API utilizando Python y SQLite",
    author="Natalia Castro",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "requests",
        "openpyxl",
        "lxml",
    ],
)