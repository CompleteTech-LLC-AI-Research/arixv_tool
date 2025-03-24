# arXiv Research Assistant

This module provides a specialized agent for interacting with the arXiv Paper Manager to search, download, and manage scientific papers from arXiv.org.

## Overview

The arXiv Research Assistant is an AI agent built using the OpenAI Agents SDK that helps users find and manage scientific papers from arXiv. It provides tools for searching, downloading, and managing papers directly from arXiv.org.

## Features

- Search for papers by topic, author, category, or keywords
- Download papers by their arXiv IDs
- List papers that have already been downloaded
- Check for updates to papers in the database
- Fetch metadata for papers that were imported without metadata

## Usage

### Direct Tool Usage

```python
from arxiv_tool.arxiv_agents import search_papers

# Search for papers on a topic
result = search_papers("quantum computing", limit=5, auto_download=True)
print(f"Found {result['total_papers']} papers")

# Access the papers
for paper in result['papers']:
    print(f"Title: {paper['title']}")
    print(f"Authors: {paper['authors']}")
    print(f"Summary: {paper.get('summary', 'No summary available')}")
    print()
```

### Using the Assistant (Requires OpenAI Agents SDK)

```python
from arxiv_tool.arxiv_agents import get_arxiv_assistant

# Get the singleton instance of the assistant
assistant = get_arxiv_assistant()

# Run a query through the assistant
response = assistant.run("Find me 3 papers about reinforcement learning")
print(response)
```

## Dependencies

- OpenAI Agents SDK (`pip install openai-agents`) - Optional, for agent functionality
- Pydantic (`pip install pydantic`) - For data validation

## Installation

Install the complete package with all dependencies:

```bash
pip install -e .[agent]
```

Or install just the basic functionality:

```bash
pip install -e .
```