# Contributing to Whale Tracker & Trading Bot

Thank you for your interest in contributing to the Whale Tracker & Trading Bot project! This document provides guidelines and instructions for contributing to this project.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork to your local machine
3. Create a new branch for your feature or bugfix
4. Install the required dependencies using `pip install -r requirements.txt`

## Development Process

### Setting Up Development Environment

1. Create a virtual environment: `python -m venv venv`
2. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and add your API keys

### Coding Standards

- Follow PEP 8 style guide for Python code
- Use 4 spaces for indentation (no tabs)
- Keep line length to a maximum of 100 characters
- Write docstrings for all functions, classes, and modules
- Include type hints where appropriate

### Adding a New Exchange

1. Create a new file in `src/trading_bot/exchanges/` named after the exchange (e.g., `kraken.py`)
2. Implement the required methods based on the `ExchangeBase` class
3. Add the exchange to the `ExchangeFactory` in `exchange_factory.py`
4. Update configuration examples in `config.json` and `.env.example`
5. Add tests for the new exchange in the `tests/` directory

### Testing

- Write unit tests for all new functionality
- Run existing tests before submitting: `python -m unittest discover tests`
- Ensure all tests pass and maintain code coverage
- Add integration tests for new features when applicable

## Pull Request Process

1. Update the README.md and documentation with details of changes
2. Update the UPGRADE_SUMMARY.md with your contributions
3. Increment version numbers in relevant files following [Semantic Versioning](https://semver.org/)
4. Create a pull request against the `main` branch
5. Ensure your PR includes:
   - A clear description of changes
   - Any relevant issue numbers
   - Updates to documentation
   - Necessary tests

## Code Review Process

All submissions require review before being merged. Reviewers will check:

- Code quality and style
- Test coverage
- Documentation
- Overall design and implementation

## Security Guidelines

- Never commit API keys or other secrets
- Use environment variables for sensitive information
- Validate all inputs, especially those from external sources
- Report security vulnerabilities via email, not as public issues

## Community and Communication

- Join our Discord server for real-time communication
- Subscribe to the mailing list for announcements
- Use GitHub issues for bug reports and feature requests
- Follow the [Code of Conduct](CODE_OF_CONDUCT.md)

## License

By contributing to this project, you agree that your contributions will be licensed under the project's [MIT License](LICENSE). 