from setuptools import setup, find_packages

from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

with open("sspike/_version.py", "r") as f:
    version = f.readline().split("=")[1].strip()


setup(
    name="sspike",
    version=version,
    author="Joe Smolsky",
    author_email="smolsky@mit.edu",
    description="simulated supernovae projectiles inducing KamLAND events",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT License",
    keywords="KamLAND kamland supernovae",
    url="https://github.com/joesmolsky/sspike",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.8",
        "Operating System :: MacOS",
        "License :: OSI Approved :: MIT License",
    ],
    install_requires=["numpy", "matplotlib", "snewpy", "plotly", "kaleido"],
    extras_require={"dev": ["pytest", "sphinx", "sphinx-rtd-theme",]},
    entry_points={"console_scripts": ["sspike=sspike.sspike:main"]},
)
