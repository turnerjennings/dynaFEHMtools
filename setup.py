from setuptools import setup, find_packages

setup(
    name="dynaFEHMtools",
    version='0.0.1.dev1',
    description='Tools for FE head model data condensation in LS-DYNA',
    url="https://github.com/turnerjennings/dynaFEHMtools",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Topic :: Scientific/Engineering"
    ],
    author='Turner Jennings',
    author_email='turner.jennings@outlook.com',
    packages=["dynaFEHMtools","dynaFEHMtools/injurymetrics"], 
    license='LICENSE.txt'
    )