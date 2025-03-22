from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="arxiv-paper-manager",
    version="1.0.0",
    author="CompleteTech LLC AI Research",
    author_email="info@completetech.ai",
    description="A powerful tool for searching, downloading, and managing arXiv research papers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CompleteTech-LLC-AI-Research/arixv_tool",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: Education",
        "Topic :: Database",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "arxiv-manager=main:main",
        ],
    },
)