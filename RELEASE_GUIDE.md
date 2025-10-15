# Release Guide - logseq-python v1.0.0a1

This guide covers the complete process for releasing logseq-python to PyPI.

## 📋 Pre-Release Checklist

### ✅ Code Quality
- [x] All core features implemented and tested
- [x] Code follows PEP 8 standards  
- [x] Type hints added throughout codebase
- [x] Comprehensive error handling implemented
- [x] Logging configured properly

### ✅ Testing
- [x] Unit tests for all core components
- [x] Integration tests for end-to-end workflows
- [x] CLI tests for command-line interface
- [x] Performance tests for large datasets
- [x] Mock tests for external service integration

### ✅ Documentation
- [x] README.md with installation and usage
- [x] PIPELINE_GUIDE.md with comprehensive documentation
- [x] LOGSEQ_DOCUMENTATION.md for Logseq integration
- [x] API reference documentation
- [x] CHANGELOG.md with release notes

### ✅ Package Configuration
- [x] pyproject.toml properly configured
- [x] Version set to 1.0.0a1 (alpha)
- [x] Dependencies correctly specified
- [x] Optional dependencies for different use cases
- [x] Entry points for CLI commands
- [x] Package metadata complete

## 🚀 Release Process

### Step 1: Environment Setup

```bash
# Install build tools
pip install --upgrade pip setuptools wheel build twine

# Install development dependencies
pip install -e .[dev,test,cli,pipeline]
```

### Step 2: Pre-Release Testing

```bash
# Run full test suite
python -m pytest tests/ -v --cov=logseq_py

# Test CLI functionality
python -m logseq_py.cli --help

# Test package installation
pip install -e .
logseq-py --version
```

### Step 3: Build Package

```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info/

# Build package
python -m build
```

Expected output files:
- `dist/logseq_python-1.0.0a1.tar.gz` (source distribution)  
- `dist/logseq_python-1.0.0a1-py3-none-any.whl` (wheel)

### Step 4: Package Validation

```bash
# Check package integrity
python -m twine check dist/*

# Test installation from built package
pip install dist/logseq_python-1.0.0a1-py3-none-any.whl
```

### Step 5: TestPyPI Upload (Recommended)

```bash
# Upload to TestPyPI first
python -m twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ logseq-python==1.0.0a1
```

### Step 6: PyPI Upload

```bash
# Upload to production PyPI
python -m twine upload dist/*

# Verify installation from PyPI
pip install logseq-python==1.0.0a1
```

## 🔧 Automated Release

Use the automated release script:

```bash
# Run automated release process
python scripts/release.py
```

This script will:
1. Clean previous builds
2. Run tests
3. Check code quality
4. Build package
5. Validate package
6. Provide upload commands

## 📦 Package Information

### Package Details
- **Name**: `logseq-python`
- **Version**: `1.0.0a1` (Alpha Release)
- **Python**: >=3.8
- **License**: MIT
- **Author**: Julio Ona <thinmanj@gmail.com>

### Installation Commands

```bash
# Basic installation
pip install logseq-python==1.0.0a1

# With CLI support
pip install logseq-python[cli]==1.0.0a1

# With pipeline support
pip install logseq-python[pipeline]==1.0.0a1

# Development installation
pip install logseq-python[dev]==1.0.0a1

# Full installation with all extras
pip install logseq-python[cli,pipeline,dev,test]==1.0.0a1
```

### Dependencies

**Core Dependencies:**
- requests>=2.25.0
- beautifulsoup4>=4.9.0
- lxml>=4.6.0
- python-dateutil>=2.8.0
- pyyaml>=6.0
- regex>=2021.4.4
- markdown>=3.3.0

**Optional Dependencies:**
- **CLI**: click>=8.0.0, rich>=13.0.0, typer>=0.9.0
- **Pipeline**: regex, markdown (included in core)
- **Development**: pytest, black, flake8, mypy, etc.

## 🎯 Release Strategy

### Alpha Release (1.0.0a1)
- **Purpose**: Initial public release for testing and feedback
- **Target Users**: Early adopters, contributors, testers
- **Features**: Complete core functionality with all major components
- **Stability**: Feature-complete but may have minor bugs

### Planned Beta Release (1.0.0b1)
- **Timeline**: After alpha feedback integration
- **Focus**: Bug fixes, performance optimization, documentation improvements
- **Target Users**: Production evaluators

### Planned Stable Release (1.0.0)
- **Timeline**: After beta stability validation
- **Focus**: Production-ready stable release
- **Target Users**: General public, production deployments

## 📈 Post-Release Tasks

### Immediate (Day 1)
- [x] Create GitHub release with changelog
- [x] Update repository README with installation instructions
- [x] Announce on relevant forums/communities
- [x] Monitor for immediate installation issues

### Short-term (Week 1)
- [ ] Monitor PyPI download statistics
- [ ] Respond to GitHub issues and discussions  
- [ ] Update documentation based on user feedback
- [ ] Fix any critical bugs discovered

### Medium-term (Month 1)
- [ ] Gather comprehensive user feedback
- [ ] Plan beta release based on feedback
- [ ] Performance optimizations
- [ ] Additional integrations

## 🐛 Known Issues

### Alpha Release Limitations
1. **API Dependencies**: Some extractors require external API keys
2. **Memory Usage**: Large graphs may need optimization settings
3. **Error Handling**: Some edge cases may not be fully covered
4. **Performance**: Not yet optimized for very large datasets

### Workarounds
- Configure API keys for full extractor functionality
- Use batching for large graph processing
- Enable verbose logging for debugging
- Monitor memory usage with large datasets

## 📞 Support

### For Users
- **Documentation**: README.md, PIPELINE_GUIDE.md
- **Issues**: https://github.com/thinmanj/logseq-python-library/issues
- **Discussions**: https://github.com/thinmanj/logseq-python-library/discussions

### For Contributors
- **Development Guide**: See README.md development section
- **Code Standards**: PEP 8, type hints, comprehensive tests
- **Pull Requests**: Welcome with proper testing

## 🎉 Release Announcement

**logseq-python 1.0.0a1 is now available on PyPI!**

This alpha release includes:
- ✅ Complete Analysis Engine with 4 advanced analyzers
- ✅ 8 specialized content extractors
- ✅ 3 intelligent content generators  
- ✅ Flexible pipeline framework
- ✅ Rich CLI interface
- ✅ Comprehensive documentation

Install now: `pip install logseq-python==1.0.0a1`

We're excited to get feedback from the community and work toward the stable 1.0 release!

---

*This release represents months of development and testing. Thank you to all early contributors and testers!*