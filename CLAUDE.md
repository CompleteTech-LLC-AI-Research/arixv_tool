# Claude Tools Configuration for arXiv Paper Download Tool

## Build/Run Commands
```bash
# Run the tool interactively
python main.py

# Search for papers with a specific query (limit 5 results by default)
python main.py search "quantum computing" --limit 10 --auto-download

# Batch download papers from a file
python main.py batch papers_to_download.txt --delay 3

# Import PDF files from a directory
python main.py import ./pdf_directory

# List downloaded papers
python main.py list

# Fetch metadata for previously imported papers
python main.py fetch-metadata

# Check for paper updates
python main.py check-updates

# Process existing directories
python main.py process
```

## Code Style Guidelines
1. **File Structure**: Start with shebang line, followed by module docstring
2. **Imports**: Standard library first, then project modules
3. **Naming**: Use snake_case for functions/variables, descriptive names
4. **Functions**: Include comprehensive docstrings (description, params, returns, exceptions)
5. **Error Handling**: Use try-except blocks with specific exceptions, return status dictionaries
6. **Documentation**: Clear docstrings for all public functions
7. **Formatting**: 4-space indentation, use f-strings for formatting
8. **Modularity**: Separate concerns into dedicated modules
9. **Returns**: Return structured data (dictionaries) with success/failure flags
10. **Parameters**: Use named parameters, provide sensible defaults

## Design Principles
- Modular design with clear separation of concerns
- Robust error handling with informative error messages
- Thorough documentation of all functionality
- User-friendly command-line interface with comprehensive help
- Consistent return values and status reporting