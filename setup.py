#!/usr/bin/env python3
"""
Setup script for LLM Hallucination Detection and Verification.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="llm-hallucination-detection-and-verification",
    version="0.1.0",
    author="Aqeeb Javeed",
    author_email="aqeebshaikh329@gmail.com",
    description="A comprehensive system for detecting and verifying LLM hallucinations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Aq03-svg/llm-hallucination-detection-and-verification",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "flake8>=6.0.0",
            "mypy>=1.4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "hallucination-detect=examples.basic_detection:main",
        ],
    },
    include_package_data=True,
    keywords="nlp llm hallucination detection verification fact-checking",
    project_urls={
        "Bug Reports": "https://github.com/Aq03-svg/llm-hallucination-detection-and-verification/issues",
        "Documentation": "https://github.com/Aq03-svg/llm-hallucination-detection-and-verification#readme",
        "Source Code": "https://github.com/Aq03-svg/llm-hallucination-detection-and-verification",
    },
)
