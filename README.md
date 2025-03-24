# arXiv Tool Package

This is the core package for the arXiv Paper Manager. It provides a set of modules
for searching, downloading, organizing, and managing research papers from arXiv.org.

## Package Structure

- `api/`: Modules for interacting with the arXiv API
- `cli/`: Command-line interface modules
- `database/`: Database interaction modules
- `models/`: Data models and handlers
- `utils/`: Utility functions

## Organization

The package follows a modular design with clear separation of concerns:

- **API Interaction**: The `api` package handles all communication with the arXiv API.
- **Database Management**: The `database` package manages the local SQLite database.
- **Command-Line Interface**: The `cli` package provides the user interface.
- **Models**: The `models` package defines data structures and handlers.
- **Utilities**: The `utils` package contains general-purpose helper functions.

## Usage

The package can be used as a library:

```python
from database import initialize_db
from api import search_arxiv
from cli import search_paper

# Initialize the database
initialize_db()

# Search for papers with a specific query
results = search_paper("Agents Graph Nueral Networks", limit=5, auto_download=True)
```

Or it can be used via the command-line interface:

```bash
python -m main search "Agents Graph Nueral Networks" --limit 5 --auto-download
```