# arXiv Paper Manager

![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.6%2B-brightgreen)
![arXiv API](https://img.shields.io/badge/arXiv-API-red)

A powerful command-line tool for effortlessly searching, downloading, organizing, and managing research papers from [arXiv.org](https://arxiv.org). Perfect for researchers, academics, and knowledge enthusiasts who need to maintain an organized local library of scientific literature.

## 🚀 Features

- **Powerful Search**: Search arXiv's extensive database using customizable queries
- **Smart Downloads**: Automatically download PDFs and extract comprehensive metadata
- **Organized Storage**: Well-structured directory system for papers with consistent naming
- **Local Database**: SQLite-powered tracking of all papers with search capabilities
- **Batch Processing**: Download multiple papers at once using batch files
- **Metadata Extraction**: Rich metadata extraction including titles, authors, abstracts, and more
- **Version Tracking**: Check for and download updates to papers in your collection
- **Import Existing PDFs**: Import and organize PDF files you already have
- **Interactive CLI**: User-friendly command-line interface for all operations

## 📋 Requirements

- Python 3.6 or higher
- No external dependencies required! (Uses Python standard library)

## 🔧 Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/CompleteTech-LLC-AI-Research/arixv_tool.git
   cd arixv_tool
   ```

2. Make the main script executable (Linux/Mac):
   ```bash
   chmod +x main.py
   ```

## 🖥️ Usage

### Interactive Mode

Start the interactive CLI by running:

```bash
python main.py
```

This opens a menu-driven interface to:
- Search for papers
- List downloaded papers
- Search your local collection
- Import PDF files
- Fetch metadata for papers
- Check for paper updates
- Batch download papers
- Process existing directories

### Command-Line Arguments

Run specific commands directly:

```bash
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

## 📁 Directory Structure

For each paper, the tool creates:

```
PAPER_ID/
├── metadata/
│   ├── authors.txt
│   ├── category.txt
│   ├── comment.txt
│   ├── doi.txt
│   ├── id.txt
│   ├── journal_ref.txt
│   ├── links.txt
│   ├── primary_category.txt
│   ├── published.txt
│   ├── summary.txt
│   ├── title.txt
│   └── updated.txt
└── pdf/
    └── PAPER_ID.pdf
```

## 🔍 Search Syntax

The search functionality supports all arXiv API query formats:

```
# Search by keyword in all fields
python main.py search "machine learning"

# Search by author
python main.py search "au:bengio"

# Search by title
python main.py search "ti:transformer"

# Search by category
python main.py search "cat:cs.AI"

# Combine search terms
python main.py search "au:hinton AND cat:cs.LG"
```

## 📊 Local Database

The tool maintains a SQLite database (`arxiv_papers.db`) that tracks:

- Paper ID and version information
- Title and authors
- Categories
- Download timestamp
- Storage location
- Metadata and PDF status

You can search this database with:

```bash
python main.py list
```

Or search for specific papers:

```
# From the interactive menu
> 3 (Search local papers)
> Enter search term: "neural networks"
```

## 📚 Batch Download

Create a text file with one arXiv ID per line:

```
2103.13630
1706.03762
quant-ph/0512258
```

Then download all papers with:

```bash
python main.py batch your_file.txt
```

## 📋 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [arXiv.org](https://arxiv.org) for providing the API and the incredible repository of research papers
- All the researchers who make their work openly accessible

---

Built with ❤️ by [CompleteTech LLC AI Research](https://github.com/CompleteTech-LLC-AI-Research)

*Note: This tool is not officially affiliated with arXiv. When using this tool, please respect arXiv's [API usage policy](https://arxiv.org/help/api/user-manual#service-constraints) and [terms of use](https://arxiv.org/help/license).*