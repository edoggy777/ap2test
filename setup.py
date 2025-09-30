from setuptools import setup, find_packages

setup(
    name="ap2test",
    version="0.1.0",
    description="CLI tool for testing Agent Payments Protocol (AP2) implementations",
    author="Evan Kirtz",
    author_email="kirtzevan@gmail.com",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "ap2test=ap2test.cli:cli",
        ],
    },
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
