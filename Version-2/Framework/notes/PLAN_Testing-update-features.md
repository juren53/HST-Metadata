# Comprehensive Testing Plan for Update Features

## Overview

This document outlines a comprehensive testing strategy for the 'Check for Updates' and 'Get Latest Updates' features in the HST Photo Framework. The plan covers unit, integration, and GUI end-to-end testing with a focus on local development workflows.

## Current State Analysis

### Existing Infrastructure
- **Testing Framework**: pytest (already in requirements.txt)
- **Current Tests**: Basic manual test (`test_version_checker.py`)
- **Architecture**: Modular design with separate components
- **Dependencies**: GitHub API, Git CLI, PyQt6

### Feature Components
- **GitHubVersionChecker**: API-based version checking (`utils/github_version_checker.py`)
- **GitUpdater**: Git-based update operations (`utils/git_updater.py`)
- **GUI Integration**: MainWindow menu handlers (`gui/main_window.py`)

## Testing Strategy

### Testing Scope
- **Comprehensive Coverage**: Unit, Integration, and GUI End-to-End tests
- **Environment**: Local development focused
- **Error Scenarios**: Happy path with basic error handling

### Test Structure
```
tests/
├── unit/
│   ├── test_github_version_checker.py
│   └── test_git_updater.py
├── integration/
│   ├── test_version_check_integration.py
│   └── test_git_update_integration.py
├── gui/
│   ├── test_check_updates_gui.py
│   └── test_get_updates_gui.py
└── conftest.py  # Shared fixtures and utilities
```

## 1. Unit Tests

### GitHubVersionChecker Tests (`test_github_version_checker.py`)

#### Core Functionality Tests
```python
def test_version_comparison():
    """Test semantic version comparison logic"""
    # Test cases: v0.1.5 vs v0.1.6, v0.1.5b vs v0.1.5, etc.

def test_api_url_construction():
    """Test GitHub API URL formation"""
    # Verify correct API URL construction from repo URL

def test_timeout_handling():
    """Test timeout behavior for API requests"""
    # Verify graceful handling of network timeouts

def test_version_parsing():
    """Test version extraction from API responses"""
    # Parse version numbers from GitHub API JSON

def test_current_version_detection():
    """Test local version reading from __init__.py"""
    # Verify correct local version detection
```

#### Edge Cases
- Version format variations (v0.1.5, 0.1.5, v0.1.5b)
- API response parsing with missing fields
- Invalid repository URLs
- Network connectivity issues

### GitUpdater Tests (`test_git_updater.py`)

#### Core Functionality Tests
```python
def test_git_repo_detection():
    """Test git repository identification"""
    # Verify detection of git vs non-git directories

def test_uncommitted_changes_detection():
    """Test detection of modified files"""
    # Check for dirty working directory detection

def test_branch_detection():
    """Test current branch identification"""
    # Verify correct branch name detection

def test_remote_url_validation():
    """Test repository URL validation"""
    # Verify remote URL parsing and validation

def test_pull_operations():
    """Test safe git pull execution"""
    # Test git pull with proper error handling
```

#### Edge Cases
- Non-git directories
- Detached HEAD state
- Missing remotes
- Network connectivity issues
- Merge conflicts

## 2. Integration Tests

### Version Check Integration (`test_version_check_integration.py`)

#### Workflow Tests
```python
def test_end_to_end_version_check():
    """Complete version check workflow"""
    # Full process from menu click to result display

def test_gui_integration_version_checker():
    """MainWindow integration testing"""
    # Verify proper GUI integration

def test_background_threading():
    """Non-blocking UI operations"""
    # Test background thread management

def test_result_handling():
    """Result processing and display"""
    # Verify proper result handling and user feedback
```

### Git Update Integration (`test_git_update_integration.py`)

#### Workflow Tests
```python
def test_git_update_workflow():
    """Complete git update process"""
    # Full workflow from menu to completion

def test_gui_integration_git_updater():
    """MainWindow integration testing"""
    # Verify proper GUI component integration

def test_update_confirmation_flow():
    """User confirmation dialog testing"""
    # Test confirmation dialog flow

def test_progress_reporting():
    """Progress indication during updates"""
    # Verify progress reporting functionality
```

## 3. GUI End-to-End Tests

### "Check for Updates" Workflow (`test_check_updates_gui.py`)

#### User Interaction Tests
```python
def test_menu_trigger_check_updates():
    """Menu item activation"""
    # Test menu item click and initialization

def test_update_available_dialog():
    """Update notification display"""
    # Test dialog when updates are available

def test_no_updates_dialog():
    """Up-to-date messaging"""
    # Test dialog when no updates available

def test_update_dialog_content():
    """Release notes and download links"""
    # Verify dialog content accuracy
```

### "Get Latest Updates" Workflow (`test_get_updates_gui.py`)

#### User Interaction Tests
```python
def test_menu_trigger_get_updates():
    """Menu item activation"""
    # Test menu item click and initialization

def test_git_repo_validation():
    """Non-git repository handling"""
    # Test behavior in non-git directories

def test_uncommitted_changes_warning():
    """Dirty state detection"""
    # Test warning dialog for uncommitted changes

def test_update_confirmation_dialog():
    """User confirmation flow"""
    # Test confirmation before pulling updates

def test_update_progress_dialog():
    """Progress indication"""
    # Test progress dialog during git operations

def test_update_completion_dialog():
    """Results reporting"""
    # Test completion dialog with results
```

## 4. Test Infrastructure

### Configuration (`pytest.ini`)
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = --verbose --tb=short
```

### Shared Fixtures (`conftest.py`)

#### Mock Fixtures
```python
@pytest.fixture
def mock_github_api_response():
    """Mock GitHub API responses for testing"""

@pytest.fixture
def mock_git_repository():
    """Mock git repository for testing"""

@pytest.fixture
def mock_qt_application():
    """Mock PyQt6 application for GUI testing"""
```

#### Test Utilities
```python
def create_temp_git_repo():
    """Create temporary git repository for testing"""

def cleanup_temp_repo():
    """Clean up temporary test repositories"""

def mock_network_responses():
    """Mock network calls and responses"""
```

## 5. Mock Strategy

### External Dependencies to Mock

#### GitHub API
- API endpoint responses
- Network error scenarios
- Timeout handling
- Rate limiting

#### Git Operations
- Subprocess calls to git
- Repository state inspection
- Remote operations
- Status reporting

#### File System
- Repository directory structure
- Configuration file access
- Version file reading

### Mock Data Sets

#### GitHub API Responses
```json
{
  "tag_name": "v0.1.6",
  "name": "Release v0.1.6",
  "body": "Release notes and changes...",
  "html_url": "https://github.com/juren53/HST-Metadata/releases/tag/v0.1.6",
  "published_at": "2026-01-15T10:00:00Z"
}
```

#### Git Repository States
- Clean repository
- Repository with uncommitted changes
- Different branch configurations
- Various remote setups

## 6. Key Test Scenarios

### Happy Path Scenarios

#### Version Check Success
1. User clicks "Check for Updates" menu
2. Background thread queries GitHub API
3. API returns newer version
4. Update dialog displays with release notes
5. User can access download links

#### Version Check Up-to-Date
1. User clicks "Check for Updates" menu
2. API returns same/older version
3. "Up to date" message displayed
4. Status bar updated accordingly

#### Git Update Success
1. User clicks "Get Latest Updates" menu
2. Git validation passes
3. Updates available confirmed
4. User confirms update
5. Git pull executes successfully
6. Results displayed to user

#### Git Update Already Current
1. User clicks "Get Latest Updates" menu
2. Git validation passes
3. No updates available
4. "Already up to date" message shown

### Basic Error Handling

#### Network Issues
- API timeout handling
- Network unreachable scenarios
- Graceful error messages

#### Repository Issues
- Non-git repository detection
- Uncommitted changes warnings
- Remote repository access issues

## 7. Implementation Phases

### Phase 1: Foundation (Week 1)
**Objectives:**
- Set up test structure and configuration
- Implement unit tests for core components
- Create mock utilities and fixtures

**Deliverables:**
- Test directory structure
- Unit tests for GitHubVersionChecker
- Unit tests for GitUpdater
- Basic mock infrastructure

### Phase 2: Integration (Week 2)
**Objectives:**
- Add integration tests for component interactions
- Test GUI threading and background operations
- Verify result handling and error cases

**Deliverables:**
- Integration tests for version checking
- Integration tests for git updating
- Threading and async operation tests
- Error handling validation

### Phase 3: GUI End-to-End (Week 3)
**Objectives:**
- Implement GUI workflow tests
- Test user interaction flows
- Verify dialog behavior and messaging

**Deliverables:**
- GUI tests for "Check for Updates" workflow
- GUI tests for "Get Latest Updates" workflow
- Dialog content validation
- User experience testing

### Phase 4: Validation (Week 4)
**Objectives:**
- Run complete test suite
- Verify coverage and functionality
- Documentation and maintenance procedures

**Deliverables:**
- Complete test suite execution
- Coverage reports
- Test documentation
- Maintenance guidelines

## 8. Success Criteria

### Coverage Requirements
- **Code Coverage**: 85%+ for update feature components
- **Function Coverage**: 100% of public APIs tested
- **Workflow Coverage**: All user workflows tested end-to-end

### Quality Requirements
- **Reliability**: All tests pass consistently in local environment
- **Maintainability**: Clear test structure and documentation
- **Performance**: Tests complete within reasonable time limits

### Documentation Requirements
- **Test Documentation**: Clear test descriptions and purpose
- **Setup Instructions**: Easy test environment setup
- **Maintenance Guide**: Guidelines for test updates

## 9. Maintenance and Evolution

### Test Maintenance
- Regular updates for new features
- Mock data updates for API changes
- Test refactoring for code changes

### Continuous Improvement
- Coverage monitoring and improvement
- Test execution time optimization
- Mock strategy refinement

### Knowledge Transfer
- Test writing guidelines
- Best practices documentation
- Training materials for team members

## 10. Risk Assessment

### Technical Risks
- **GUI Testing Complexity**: PyQt6 GUI testing challenges
- **Mock Maintenance**: Keeping mocks in sync with real APIs
- **Test Environment**: Ensuring consistent test environments

### Mitigation Strategies
- Start with simple GUI tests and increase complexity gradually
- Regular mock validation against real APIs
- Use containerized test environments if needed

## Conclusion

This comprehensive testing plan provides a structured approach to validating the update features of the HST Photo Framework. By implementing unit, integration, and GUI tests, we can ensure reliable functionality and a smooth user experience for both update workflows.

The modular implementation approach allows for incremental development while maintaining focus on the most critical user scenarios. The emphasis on local development testing ensures the tests are practical and immediately useful for the development team.

Regular execution of these tests will help maintain code quality and prevent regressions in the update functionality as the framework continues to evolve.