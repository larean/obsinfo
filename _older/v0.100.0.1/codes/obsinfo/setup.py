import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="obsinfo",
    version="0.100.0.1",
    author="Wayne Crawford",
    author_email="crawford@ipgp.fr",
    description="Tools for processing OBS metadata and data information",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/obsinfo",
    packages=setuptools.find_packages(),
    install_requires=[
          'obspy',
      ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)