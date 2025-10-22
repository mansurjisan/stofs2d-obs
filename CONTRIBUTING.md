# Contributing to STOFS2D-OBS

Thank you for considering contributing to STOFS2D-OBS! This document provides guidelines for contributing to the project.

---

## Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/stofs2d-obs.git
cd stofs2d-obs
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate # On Windows: .venv\Scripts\activate
```

### 3. Install Development Dependencies

```bash
pip install -e ".[dev]"
```

This installs:
- The package in editable mode
- All dependencies
- Development tools (pytest, black, flake8, isort)

---

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

Edit code in `stofs2d_obs/` directory

### 3. Run Tests

```bash
# Fast unit tests
pytest tests/ -v -m "unit and not slow"

# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=stofs2d_obs --cov-report=html
```

### 4. Format Code

```bash
# Auto-format with black
black stofs2d_obs/

# Sort imports
isort stofs2d_obs/

# Check linting
flake8 stofs2d_obs/
```

### 5. Commit Changes

```bash
git add .
git commit -m "Add feature: description of changes"
```

###6. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

---

## Code Style

### Python Style Guide

- **PEP 8** compliance
- **Line length:** 100 characters
- **Formatter:** black
- **Import sorting:** isort

### Automatic Formatting

```bash
# Format everything
black stofs2d_obs/
isort stofs2d_obs/
```

### Code Quality Checks

```bash
# Linting
flake8 stofs2d_obs/

# Type checking (optional)
mypy stofs2d_obs/
```

---

## Writing Tests

### Test Location

- Add tests to `tests/` directory
- Name test files: `test_*.py`
- Name test functions: `test_*`

### Test Example

```python
import pytest
from stofs2d_obs import Fort61Reader

def test_fort61_reader_opens_file(mock_fort61_file):
 """Test that Fort61Reader opens a file correctly"""
 with Fort61Reader(mock_fort61_file) as reader:
 assert reader.ds is not None
```

### Running Tests

```bash
# All tests
pytest tests/

# Specific file
pytest tests/test_fort61.py

# Specific test
pytest tests/test_fort61.py::test_fort61_reader_opens_file

# With coverage
pytest tests/ --cov=stofs2d_obs
```

---

## Pull Request Guidelines

### Before Submitting

1. All tests pass
2. Code is formatted (black, isort)
3. No linting errors (flake8)
4. Coverage doesn't decrease
5. Documentation is updated

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added
- [ ] Coverage maintained/improved

## Checklist
- [ ] Code formatted with black
- [ ] Imports sorted with isort
- [ ] No flake8 errors
- [ ] Documentation updated
```

---

## Commit Messages

### Format

```
type: Short description (50 chars or less)

Longer description if needed (wrap at 72 chars)
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build/tooling changes

### Examples

```
feat: Add batch processing CLI option

Implements --batch flag to process multiple stations
automatically with CSV and HTML report generation.

fix: Handle timezone mismatch in data alignment

Adds automatic timezone localization when aligning
model and observation timeseries data.

docs: Update README with CLI examples

Adds comprehensive examples for single station
and batch processing modes.
```

---

## Documentation

### Docstring Format

Use Google-style docstrings:

```python
def function_name(param1, param2):
 """
 Brief description of function.

 Longer description if needed.

 Args:
 param1: Description of param1
 param2: Description of param2

 Returns:
 Description of return value

 Raises:
 ValueError: When something goes wrong
 """
 pass
```

### Adding Examples

Include examples in docstrings:

```python
def calculate_rmse(model, obs):
 """
 Calculate Root Mean Square Error.

 Example:
 >>> model = np.array([1.0, 2.0, 3.0])
 >>> obs = np.array([1.1, 2.1, 2.9])
 >>> rmse = calculate_rmse(model, obs)
 >>> print(f"{rmse:.3f}")
 0.100
 """
 pass
```

---

## Reporting Issues

### Bug Reports

Include:
1. **Description** - What happened?
2. **Expected behavior** - What should happen?
3. **Steps to reproduce** - How to recreate?
4. **Environment** - OS, Python version, package version
5. **Code example** - Minimal reproducing example

### Feature Requests

Include:
1. **Description** - What feature?
2. **Use case** - Why is it needed?
3. **Proposed solution** - How should it work?
4. **Alternatives** - Other approaches considered?

---

## Release Process

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes

### Creating a Release

1. Update version in `pyproject.toml` and `setup.py`
2. Update `CHANGELOG.md`
3. Commit: `git commit -m "chore: Bump version to X.Y.Z"`
4. Tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
5. Push: `git push && git push --tags`
6. Create release on GitHub
7. CI/CD automatically publishes to PyPI

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors.

### Expected Behavior

- Be respectful and considerate
- Welcome newcomers
- Accept constructive criticism
- Focus on what's best for the community

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Public or private harassment
- Publishing others' private information

---

## Getting Help

### Documentation

- README.md - Package overview
- CI_CD_SETUP.md - CI/CD documentation
- UNIT_TESTS.md - Testing documentation
- Examples in `examples/` directory

### Contact

- **Issues:** https://github.com/YOUR_USERNAME/stofs2d-obs/issues
- **Discussions:** https://github.com/YOUR_USERNAME/stofs2d-obs/discussions

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to STOFS2D-OBS! 
