# Claude Tools Configuration for arXiv Paper Manager

## Build/Run Commands

```bash
# Install package in development mode
pip install -e .

# Install optional dependencies
pip install -e .[sdk]     # For SDK metadata output
pip install -e .[agent]   # For agent integration (OpenAI Agents SDK)
pip install -e .[pdf]     # For PDF extraction features

# Run as package CLI 
arxiv-tool search "quantum computing" --limit 5 --auto-download

# Run as Python script
python main.py search "quantum computing" --limit 5
python -m arxiv_tool.main search "quantum computing" --limit 5

# Test the agent
python -m tests.test_agent

# Run tests
pytest tests/                          # Run all tests
pytest tests/test_arxiv_agent.py       # Run specific test file
pytest tests/test_agent.py::test_function_name  # Run single test
pytest --cov=arxiv_tool tests/         # Test with coverage

# Recommended linting tools
flake8 arxiv_tool/                     # Code linting
black arxiv_tool/                      # Code formatting
isort arxiv_tool/                      # Import sorting
mypy arxiv_tool/                       # Type checking
```

## Code Style Guidelines

1. **Files**: Start with shebang + docstring describing file's purpose
2. **Imports**: Standard library → third-party → project modules, alphabetized
3. **Naming**: `snake_case` for variables/functions, `PascalCase` for classes
4. **Functions**: Include docstrings with parameters, return values, exceptions
5. **Error Handling**: Use specific exceptions and structured result dictionaries:
   ```python
   try:
       # code
   except SpecificException as e:
       return {"success": False, "error": str(e)}
   return {"success": True, "data": result}
   ```
6. **Types**: Use type annotations for function parameters and return values
7. **Formatting**: 4-space indentation, line length ≤ 88 chars, f-strings preferred
8. **Documentation**: Clear docstrings for all public functions/methods

## Package Organization

```
arxiv_tool/
├── __init__.py
├── api/              # arXiv API interaction
├── arxiv_agents/     # AI agent integration
├── cli/              # Command-line interface
├── config.py         # Configuration settings
├── database/         # Database operations
├── models/           # Data models and processors
├── tests/            # Test scripts
└── utils/            # Utility functions
```

## AI Agent Implementation

The arXiv Research Assistant is implemented in the `arxiv_agents` module and uses the OpenAI Agents SDK. Key components:

1. **ArxivResearchAssistant**: Main agent class that configures and runs the agent
2. **Function Tools**:
   - `search_arxiv_papers`: Find papers on arXiv
   - `list_arxiv_papers`: List downloaded papers
   - `download_arxiv_papers`: Download papers by ID
   - `check_for_paper_updates`: Check for updates
   - `fetch_paper_metadata`: Get metadata for imported papers

3. **Direct Tool Usage**: The `search_papers` function allows direct use of the search functionality without an agent.

4. **Singleton Pattern**: The `get_arxiv_assistant()` function returns a singleton instance of the assistant.

## Testing

The `tests` directory contains test scripts for various components:

1. **test_agent.py**: Basic tests for the ArXiv Research Assistant
2. **test_arxiv_agent.py**: Tests for agent-specific functionality
3. **test_refactored_agent.py**: Tests for the refactored agent implementation
4. **test_wrapper.py**: Tests for the agent wrapper functionality

The CLI follows a subcommand pattern and functions are designed to be used both from CLI and programmatically. SDK metadata integration, agent wrapper, and batch processing are documented in the README. When using the API, handle errors gracefully and return structured data with success/failure flags.