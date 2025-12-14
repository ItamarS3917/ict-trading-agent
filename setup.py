"""
Setup configuration for ICT Trading Agent
"""

from setuptools import setup, find_packages
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ict-trading-agent",
    version="1.0.0",
    author="Itamar Shealtiel",
    author_email="itamarshealtiel1@gmail.com",
    description="Algorithmic trading analysis tool implementing Inner Circle Trader concepts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ItamarS3917/ict-trading-agent",
    project_urls={
        "Bug Tracker": "https://github.com/ItamarS3917/ict-trading-agent/issues",
        "Documentation": "https://github.com/ItamarS3917/ict-trading-agent#readme",
        "Source Code": "https://github.com/ItamarS3917/ict-trading-agent",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ict-agent=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["config/*.yaml"],
    },
    keywords=[
        "trading",
        "algorithmic-trading",
        "ict",
        "inner-circle-trader",
        "technical-analysis",
        "backtesting",
        "market-analysis",
        "trading-strategy",
        "fair-value-gap",
        "order-blocks",
        "nasdaq",
        "futures",
    ],
    zip_safe=False,
)
