"""
NetFlux5G - 5G Network Simulation Tool
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open(os.path.join(this_directory, 'requirements.txt'), encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="netflux5g",
    version="1.0.0",
    author="NetFlux5G Team",
    author_email="contact@netflux5g.dev",
    description="5G Network Simulation Tool with Docker Container Support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/netflux5g/netflux5g",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
        "Topic :: System :: Networking",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["assets/*", "assets/**/*", "config/*", "config/**/*"],
    },
    data_files=[
        ("scripts", ["scripts/health_check.py", "scripts/deploy_production.sh", "scripts/deploy_production.ps1"]),
        ("", ["production.cfg", "PRODUCTION_CHECKLIST.md"]),
    ],
    entry_points={
        "console_scripts": [
            "netflux5g=main:main",
        ],
    },
    keywords="5g, simulation, docker, networking, open5gs, ueransim",
    project_urls={
        "Bug Reports": "https://github.com/netflux5g/netflux5g/issues",
        "Source": "https://github.com/netflux5g/netflux5g",
        "Documentation": "https://github.com/netflux5g/netflux5g/wiki",
    },
)
