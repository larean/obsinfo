import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="obsinfo",
    version="0.100.0.2",
    author="Wayne Crawford",
    author_email="crawford@ipgp.fr",
    description="Tools for docuenting ocean bottom seismometer experiement parameters and creating data & metadata",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/obsinfo",
    packages=setuptools.find_packages(),
    install_requires=[
          'obspy',
          'pyyaml'
      ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)