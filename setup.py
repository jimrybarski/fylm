from setuptools import setup, find_packages

setup(
    name="fylm",
    packages=find_packages(),
    version="0.2.0",
    install_requires=[
        'six',
        'Cython',
        'numpy',
        'scipy',
        'matplotlib',
    ],
)