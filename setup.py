import setuptools
import sys

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

cmdclass = {}
command_options = {}


name = "certi"
version = "0.1.0"


setuptools.setup(
    name=name,
    version=version,
    author="Eloy Perez",
    author_email="zer1t0ps@protonmail.com",
    description="Tool to ask certificates to ADCS and discover templates",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "certi.py = certilib.main:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: Linux",
    ],
    cmdclass=cmdclass,
    command_options=command_options,
)
