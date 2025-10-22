# CI/CD Setup - Complete

## Overview

Comprehensive CI/CD pipeline has been **successfully configured** using GitHub Actions!

**Status:** Ready to Deploy
**Platform:** GitHub Actions
**Workflows:** 2 automated workflows
**Coverage:** Integrated with Codecov

---

## Workflows Implemented

### 1. CI Workflow (`.github/workflows/ci.yml`) 

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

**Jobs:**

#### A. Test Job
- **Runs on:** Ubuntu Latest
- **Python versions:** 3.8, 3.9, 3.10, 3.11, 3.12
- **Actions:**
 - Install dependencies
 - Run unit tests (fast)
 - Run full tests with coverage (Python 3.12 only)
 - Upload coverage to Codecov

#### B. Lint Job
- **Runs on:** Ubuntu Latest
- **Python version:** 3.12
- **Actions:**
 - Check code with flake8
 - Check formatting with black
 - Check import sorting with isort

#### C. Build Job
- **Runs on:** Ubuntu Latest
- **Python version:** 3.12
- **Actions:**
 - Build package with `build`
 - Verify package with `twine`
 - Upload build artifacts

---

### 2. Publish Workflow (`.github/workflows/publish.yml`) 

**Triggers:**
- GitHub release published

**Jobs:**

#### Publish Job
- **Runs on:** Ubuntu Latest
- **Python version:** 3.12
- **Actions:**
 - Build package
 - Publish to Test PyPI (for pre-releases)
 - Publish to PyPI (for full releases)

**Security:** Uses trusted publishing (no API tokens needed)

---

## Configuration Files

### 1. `.github/workflows/ci.yml`
Main CI pipeline configuration

### 2. `.github/workflows/publish.yml`
PyPI publishing configuration

### 3. `.flake8`
Flake8 linting configuration
```ini
[flake8]
max-line-length = 100
extend-ignore = E203, W503
exclude = .git, __pycache__, build, dist, tests/
```

### 4. `pyproject.toml` (additions)
Black, isort, pytest, coverage configuration

### 5. `.gitignore`
Files to exclude from version control

---

## Status Badges

Added to README.md:

```markdown
[![CI](https://github.com/oceanmodeling/stofs2d-obs/actions/workflows/ci.yml/badge.svg)](...)
[![codecov](https://codecov.io/gh/oceanmodeling/stofs2d-obs/branch/main/graph/badge.svg)](...)
[![PyPI version](https://badge.fury.io/py/stofs2d-obs.svg)](...)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](...)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](...)
```

These badges will show:
- CI build status
- Code coverage percentage
- Latest PyPI version
- Python version support
- License type

---

## How It Works

### On Every Push/PR

```
1. Checkout code
2. Set up Python (3.8, 3.9, 3.10, 3.11, 3.12)
3. Install dependencies
4. Run unit tests
5. Run full tests + coverage (3.12 only)
6. Upload coverage to Codecov
7. Lint code (separate job)
8. Build package (separate job)
```

### On Release

```
1. Checkout code
2. Set up Python 3.12
3. Build package
4. Check package with twine
5. Publish to PyPI (or Test PyPI for pre-releases)
```

---

## Setting Up on GitHub

### Step 1: Initialize Git Repository

```bash
cd /mnt/c/Searvey_Fort61
git init
git add .
git commit -m "Initial commit with CI/CD"
```

### Step 2: Create GitHub Repository

1. Go to https://github.com/new
2. Create repository: `stofs2d-obs`
3. Don't initialize with README (we already have one)

### Step 3: Push to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/stofs2d-obs.git
git branch -M main
git push -u origin main
```

### Step 4: Enable Codecov (Optional)

1. Go to https://codecov.io
2. Sign in with GitHub
3. Add your repository
4. No token needed - GitHub Actions integration is automatic

### Step 5: Set Up PyPI Publishing (When Ready)

#### For Trusted Publishing (Recommended):

1. Go to https://pypi.org/manage/account/publishing/
2. Add a new publisher:
 - **PyPI Project Name:** `stofs2d-obs`
 - **Owner:** Your GitHub username/organization
 - **Repository name:** `stofs2d-obs`
 - **Workflow name:** `publish.yml`
 - **Environment name:** (leave empty)

#### Alternative - Using API Token:

1. Generate PyPI API token at https://pypi.org/manage/account/token/
2. Add as GitHub secret: `PYPI_API_TOKEN`
3. Modify workflow to use token

---

## Testing CI/CD Locally

### 1. Test Code Quality Checks

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run flake8
flake8 stofs2d_obs/ --count --max-line-length=100

# Check formatting with black
black --check --line-length 100 stofs2d_obs/

# Check import sorting
isort --check-only --profile black stofs2d_obs/
```

### 2. Test Package Build

```bash
# Install build tools
pip install build twine

# Build package
python -m build

# Check package
twine check dist/*
```

### 3. Run Tests

```bash
# Fast unit tests
pytest tests/ -v -m "unit and not slow"

# With coverage
pytest tests/ --cov=stofs2d_obs --cov-report=html
```

---

## Automatic Code Formatting

To automatically format code before committing:

```bash
# Format with black
black stofs2d_obs/

# Sort imports
isort stofs2d_obs/

# Then commit
git add .
git commit -m "Format code"
```

---

## Workflow Triggers

### CI Workflow Runs On:

```yaml
on:
 push:
 branches: [ main, develop ]
 pull_request:
 branches: [ main, develop ]
```

### Publish Workflow Runs On:

```yaml
on:
 release:
 types: [published]
```

---

## Matrix Testing

The CI runs tests on **5 Python versions** simultaneously:

| Python Version | Status |
|----------------|--------|
| 3.8 | Tested |
| 3.9 | Tested |
| 3.10 | Tested |
| 3.11 | Tested |
| 3.12 | Tested + Coverage |

This ensures compatibility across all supported Python versions!

---

## Coverage Integration

### Codecov Integration

**Automatic:** Coverage is uploaded to Codecov on every push to main/develop.

**Benefits:**
- Visual coverage reports
- Coverage trends over time
- Line-by-line coverage
- PR comments with coverage changes

**View coverage:**
https://codecov.io/gh/YOUR_USERNAME/stofs2d-obs

---

## Build Artifacts

After successful build, artifacts are uploaded:

- **Location:** GitHub Actions → Workflow run → Artifacts
- **Contains:** `dist/` directory with:
 - `.tar.gz` source distribution
 - `.whl` wheel distribution

---

## Publishing Releases

### Create a Release

```bash
# Tag the release
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin v0.1.0

# Or create release on GitHub:
# Go to: https://github.com/YOUR_USERNAME/stofs2d-obs/releases/new
```

### Pre-release (Test PyPI)

1. Create release with "This is a pre-release" checked
2. Workflow publishes to Test PyPI automatically

### Full Release (PyPI)

1. Create release without pre-release checkbox
2. Workflow publishes to PyPI automatically

---

## Monitoring CI/CD

### View Workflow Runs

https://github.com/YOUR_USERNAME/stofs2d-obs/actions

### View Build Status

Check the badges in README.md - they update automatically!

### View Coverage

https://codecov.io/gh/YOUR_USERNAME/stofs2d-obs

---

## Troubleshooting

### Tests Fail on CI but Pass Locally

**Possible causes:**
- Environment differences
- Missing dependencies
- Timezone issues

**Solution:**
```bash
# Run tests in clean environment
python -m venv clean_env
source clean_env/bin/activate # or clean_env\Scripts\activate on Windows
pip install -e .
pytest tests/
```

### Coverage Upload Fails

**Solution:**
- Codecov token not needed with GitHub Actions
- Check that `codecov/codecov-action@v4` is used
- Verify repository is added to Codecov

### PyPI Publishing Fails

**Common issues:**
1. **Package name already exists** - Choose different name
2. **Version already published** - Bump version number
3. **Authentication failed** - Set up trusted publishing or add token

---

## Next Steps

### After Pushing to GitHub

1. **Enable branch protection** (optional):
 - Go to Settings → Branches
 - Add rule for `main` branch
 - Require status checks to pass
 - Require PR reviews

2. **Set up Codecov** (optional):
 - Sign in at codecov.io
 - Add repository

3. **Create first release**:
 - Tag version: `git tag v0.1.0`
 - Push tag: `git push origin v0.1.0`
 - Create release on GitHub

---

## Files Created

```
.github/
└── workflows/
 ├── ci.yml # Main CI pipeline
 └── publish.yml # PyPI publishing

.flake8 # Flake8 configuration
.gitignore # Git ignore rules
pyproject.toml # Updated with tool configs
README.md # Updated with badges
```

---

## Summary

### CI/CD Features 

- Automated testing on 5 Python versions
- Code quality checks (flake8, black, isort)
- Coverage reporting with Codecov
- Package building and validation
- Automated PyPI publishing
- Status badges in README
- Build artifacts storage
- Pre-release support

### Benefits

1. **Quality Assurance** - Every change is tested
2. **Cross-Platform** - Tests on multiple Python versions
3. **Code Style** - Consistent formatting enforced
4. **Coverage Tracking** - Know what's tested
5. **Easy Publishing** - One-click releases
6. **Professional** - Industry-standard CI/CD

---

**CI/CD Status:** Ready for Production!

Once pushed to GitHub, the CI pipeline will run automatically on every commit and pull request.

---

**Created:** 2025-10-22
**Status:** Complete and Ready
**Platform:** GitHub Actions
**Next:** Push to GitHub to activate workflows!
