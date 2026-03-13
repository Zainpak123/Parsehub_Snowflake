# Contributing to ParseHub Dashboard

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the ParseHub Dashboard project.

## Code of Conduct

- Be respectful and inclusive
- Help each other grow
- Report issues professionally
- Focus on the code, not the person

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in Issues
2. If not, create a new issue with:
   - Clear title describing the bug
   - Detailed reproduction steps
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)
   - Relevant logs/screenshots

### Suggesting Features

1. Check existing issues for similar suggestions
2. Create new issue with:
   - Clear title describing the feature
   - Detailed description of the use case
   - Why this feature would be useful
   - Possible implementation approach (optional)

### Submitting Code

1. **Fork** the repository
2. **Create a branch** for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make changes** following the code style guide
4. **Add tests** for your changes
5. **Run tests** to ensure nothing breaks:
   ```bash
   pytest backend/tests/
   ```
6. **Commit** with clear, descriptive messages:
   ```bash
   git commit -m "Add feature: brief description"
   ```
7. **Push** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
8. **Create Pull Request** to `main` branch with:
   - Clear title
   - Detailed description of changes
   - Reference to related issue(s)
   - Checklist of tests completed

## Development Setup

### Requirements

- Python 3.12+
- Node.js 18+
- Docker & Docker Compose (for containerized testing)

### Backend Setup

```bash
# Create virtual environment
cd backend
python -m venv venv_sf
source venv_sf/bin/activate  # On Windows: venv_sf\Scripts\activate

# Install dependencies
pip install -r requirements-python312.txt

# Install dev dependencies
pip install -e ".[dev]"

# Configure environment
cp src/config/.env.example src/config/.env
# Edit .env with your configuration

# Run tests
pytest
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local

# Start dev server
npm run dev
```

## Code Style Guide

### Python

- **Style**: PEP 8 with Black formatter
- **Line Length**: 100 characters
- **Type Hints**: Required for public functions
- **Docstrings**: Required for all modules and functions

Format code:
```bash
black backend/src/
isort backend/src/
mypy backend/src/
```

Example:
```python
def process_project_data(project_id: int, data: dict) -> bool:
    """
    Process project data and store in database.
    
    Args:
        project_id: The project ID
        data: The data dictionary to process
    
    Returns:
        True if successful, False otherwise
    
    Raises:
        ValueError: If project_id is invalid
    """
    if project_id <= 0:
        raise ValueError("project_id must be positive")
    
    # Implementation
    return True
```

### JavaScript/TypeScript

- **Style**: Prettier configured
- **Linting**: ESLint
- **Type Checking**: TypeScript strict mode

Format code:
```bash
cd frontend
npm run lint
npm run format
```

### Commit Messages

Use conventional commits:
```
type(scope): subject

Body explaining the change...

Closes #issueNumber
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting/style changes
- `refactor`: Code refactoring
- `test`: Adding/updating tests
- `chore`: Build/dependency updates

Example:
```
feat(api): add project analytics endpoint

Implements GET /api/analytics/:projectId to retrieve
project analytics data including run statistics,
data volume trends, and performance metrics.

Closes #123
```

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run specific test file
pytest tests/test_api.py

# Run with coverage
pytest --cov=src tests/

# Run specific test function
pytest tests/test_api.py::test_get_projects
```

### Frontend Tests

```bash
cd frontend

# Run tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test
npm test -- auth.test.ts
```

### Integration Tests

```bash
# Using Docker Compose
docker-compose up -d

# Test API
curl http://localhost:5000/health
curl http://localhost:3000

# Cleanup
docker-compose down
```

## Pull Request Process

1. **Update tests** for any new functionality
2. **Update documentation** if needed
3. **Ensure CI passes** - all tests must pass
4. **Request review** from maintainers
5. **Address feedback** from code review
6. **Squash commits** before merging (optional)
7. **Merge** once approved

### PR Checklist

- [ ] Tests pass locally
- [ ] Code follows style guide
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] No breaking changes (or noted in title)
- [ ] References related issues

## Documentation

When adding features or changing behavior:

1. **Update README.md** if it affects users
2. **Add docstrings** to code
3. **Update API docs** if endpoints change
4. **Add examples** for complex features
5. **Update CHANGELOG.md** for releases

## Branching Strategy

```
main
  ├── feature/user-authentication
  ├── fix/database-connection
  ├── docs/api-documentation
  └── release/v1.0.0
```

## Release Process

1. Create version branch: `git checkout -b release/v1.2.0`
2. Update version in `pyproject.toml`, `package.json`
3. Update `CHANGELOG.md`
4. Create PR for release
5. After merge, tag release: `git tag v1.2.0`
6. Push tag: `git push origin v1.2.0`
7. GitHub Actions would create release automatically

## Performance Guidelines

- Minimize database queries (use caching)
- Optimize loops and conditionals
- Use background jobs for heavy operations
- Profile code before optimizing
- Consider scalability from the start

## Security Guidelines

- Never commit secrets or credentials
- Use environment variables for configuration
- Validate all user inputs
- Sanitize database queries
- Use HTTPS in production
- Follow OWASP guidelines

## Questions or Need Help?

- Check [GitHub Discussions](https://github.com/yourorg/parsehub-dashboard/discussions)
- Open an issue with your question
- Contact maintainers: team@example.com
- Review existing documentation

## Recognition

Contributors will be recognized in:
- `CONTRIBUTORS.md`
- Release notes for significant contributions
- Project README (with permission)

---

**Thank you for contributing to ParseHub Dashboard!** 🎉

**Last Updated:** March 8, 2026
