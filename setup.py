from setuptools import setup, find_packages


setup(
    name="TidyTuesday",
    version="1.0",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "pywaffle",
        "requests",
        "seaborn",
    ]
)