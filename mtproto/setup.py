import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mtProto",
    version="0.0.1",
    author="Bryce Cloke",
    author_email="bdc4",
    description="A prototype for MT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bdc4/py-files",
    packages=setuptools.find_packages(),
    package=['mtproto'],
    package_data={'': ['data/*']},
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: All Rights Reserved",
        "Operating System :: MacOS",
    ),
)
