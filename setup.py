"""
Setup script for stofs2d-obs package

For modern installations, use pyproject.toml
This file is provided for backward compatibility.
"""

from setuptools import setup, find_packages

# Read the contents of README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="stofs2d-obs",
    version="0.1.0",
    author="STOFS2D Validation Team",
    description="Compare STOFS2D model output with CO-OPS tide gauge observations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/oceanmodeling/stofs2d-obs",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Oceanography",
    ],
    python_requires=">=3.9",
    install_requires=[
        "netCDF4>=1.6.0",
        "matplotlib>=3.5.0",
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "searvey>=0.3.15",
        "geopandas>=0.10.0",
        "shapely>=1.8.0",
        "pytz",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme",
        ],
    },
    entry_points={
        "console_scripts": [
            "stofs2d-compare=stofs2d_obs.cli:main",
        ],
    },
)
