# Contributing to Another Doctor

Thank you for your interest in contributing to Another Doctor! This guide will help you get started with contributing to our medical specialist matching platform.

## 🌟 Ways to Contribute

- **🐛 Report bugs** - Help us identify and fix issues
- **💡 Suggest features** - Share ideas for improvements
- **📝 Improve documentation** - Make our docs clearer and more comprehensive
- **🔧 Submit code** - Fix bugs or implement new features
- **🧪 Write tests** - Improve our test coverage
- **🎨 Design improvements** - Enhance user experience and accessibility

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ and pnpm 8+
- Python 3.11+
- Docker and Docker Compose
- Git

### Setup Development Environment

1. **Fork the repository** on GitHub
2. **Clone your fork**:
   ```bash
   git clone https://github.com/your-username/another-doctor.git
   cd another-doctor
   ```

3. **Set up the development environment**:
   ```bash
   make setup
   make install-all
   make dev-up
   ```

4. **Verify everything works**:
   ```bash
   make test-all
   make lint-all
   ```

## 🔀 Development Workflow

### 1. Create a Branch

Create a feature branch from `main`:

```bash
git checkout main
git pull origin main
git checkout -b feature/your-feature-name
```

### Branch Naming Convention

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring
- `test/description` - Adding or updating tests

### 2. Make Your Changes

#### Code Style Guidelines

**TypeScript/JavaScript:**
- Use TypeScript for all new code
- Follow ESLint configuration
- Use meaningful variable names
- Add JSDoc comments for public APIs

**Python:**
- Follow PEP 8
- Use type hints for all functions
- Use descriptive variable names
- Add docstrings for all public functions

#### Commit Message Format

Use [Conventional Commits](https://conventionalcommits.org/) format:

```
type(scope): description

[optional body]

[optional footer]
```

**Examples:**
```
feat(matching): add hybrid vector search algorithm
fix(api): handle edge case in case parsing
docs(readme): update installation instructions
refactor(db): optimize doctor query performance
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### 3. Test Your Changes

Before submitting, ensure:

```bash
# Run all tests
make test-all

# Check code quality
make lint-all

# Type checking
pnpm type-check

# Test specific component
cd apps/backend && python -m pytest tests/test_your_feature.py
```

### 4. Submit a Pull Request

1. **Push your branch**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request** on GitHub
3. **Fill out the PR template** completely
4. **Request reviews** from maintainers

## 🧪 Writing Tests

### Frontend Tests (Jest + React Testing Library)

```typescript
// apps/frontend/src/components/__tests__/YourComponent.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { YourComponent } from '../YourComponent';

describe('YourComponent', () => {
  it('should render correctly', () => {
    render(<YourComponent />);
    expect(screen.getByRole('button')).toBeInTheDocument();
  });
});
```

### Backend Tests (pytest)

```python
# apps/backend/tests/test_your_feature.py
import pytest
from app.services.your_service import YourService

def test_your_function():
    service = YourService()
    result = service.your_function("test_input")
    assert result == "expected_output"

@pytest.mark.asyncio
async def test_async_function():
    service = YourService()
    result = await service.async_function()
    assert result is not None
```

### Integration Tests

```python
# apps/backend/tests/integration/test_api_integration.py
def test_case_creation_flow(client, db_session):
    # Test full case creation workflow
    response = client.post("/api/v1/cases", json={
        "raw_text": "Patient has condition X",
        "title": "Test Case"
    })
    assert response.status_code == 201
    assert "case_id" in response.json()
```

## 🏗️ Architecture Guidelines

### Code Organization

```
apps/
├── frontend/          # Next.js application
│   ├── src/app/       # App router pages
│   ├── src/components/# Reusable React components
│   └── src/lib/       # Frontend utilities
├── backend/           # FastAPI application  
│   ├── app/api/       # API route handlers
│   ├── app/services/  # Business logic services
│   ├── app/models/    # Database models (SQLAlchemy)
│   └── app/schemas/   # Request/response schemas (Pydantic)
└── workers/           # Background job processors
```

### Design Principles

1. **Separation of Concerns**: Keep business logic in services, not controllers
2. **Dependency Injection**: Use FastAPI's dependency system
3. **Type Safety**: Use TypeScript and Python type hints extensively  
4. **Error Handling**: Implement comprehensive error handling
5. **Security First**: Validate all inputs, sanitize outputs
6. **PHI Protection**: Never log or expose patient data

### Database Guidelines

- Use Alembic migrations for all schema changes
- Include both `upgrade()` and `downgrade()` functions
- Test migrations on staging data first
- Use UUIDs for primary keys
- Index commonly queried fields

## 🔐 Security Guidelines

### PHI Protection

- **Never** include PHI in logs
- **Always** de-identify data before LLM processing
- Use row-level security where appropriate
- Implement audit logging for PHI access

### Input Validation

```python
# Use Pydantic for validation
from pydantic import BaseModel, validator

class CaseCreateRequest(BaseModel):
    raw_text: str
    title: Optional[str] = None
    
    @validator('raw_text')
    def validate_text(cls, v):
        if len(v) < 10:
            raise ValueError('Text too short')
        return v
```

### Authentication

- Use JWT tokens with appropriate expiration
- Validate tokens on every request
- Implement proper RBAC (Role-Based Access Control)

## 📚 Documentation Standards

### Code Documentation

**TypeScript:**
```typescript
/**
 * Validates case JSON against schema
 * @param caseData - The case data to validate
 * @returns Validated case object
 * @throws {ValidationError} When case data is invalid
 */
export function validateCase(caseData: unknown): CaseJSON {
  return CaseJSONSchema.parse(caseData);
}
```

**Python:**
```python
def parse_medical_text(self, text: str) -> Dict[str, Any]:
    """
    Parse medical text into structured CaseJSON format.
    
    Args:
        text: Raw medical text to parse
        
    Returns:
        Dictionary containing structured case data
        
    Raises:
        ValidationError: If text cannot be parsed
    """
    pass
```

### API Documentation

Update OpenAPI schemas when changing endpoints:

```python
@router.post("/cases", response_model=Case, status_code=201)
async def create_case(
    case_data: CaseCreate,
    db: Session = Depends(get_db)
) -> Case:
    """
    Create a new medical case.
    
    - **raw_text**: The raw medical text to process
    - **title**: Optional case title
    """
    pass
```

## 🐛 Reporting Issues

### Bug Reports

When reporting bugs, include:

1. **Clear description** of the issue
2. **Steps to reproduce** the problem
3. **Expected vs actual behavior**
4. **Environment details** (OS, browser, etc.)
5. **Screenshots** if applicable
6. **Error logs** if available

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md).

### Feature Requests

When requesting features, include:

1. **Problem description** - what need does this solve?
2. **Proposed solution** - how should it work?
3. **Use cases** - who would use this and how?
4. **Alternatives considered** - other solutions you've thought of

Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md).

## 👥 Code Review Process

### For Contributors

1. **Self-review** your code before submitting
2. **Write descriptive PR descriptions** using the template
3. **Respond promptly** to review feedback
4. **Update documentation** if needed
5. **Squash commits** if requested

### Review Criteria

Code reviews focus on:

- **Functionality**: Does it work as intended?
- **Security**: Are there any security vulnerabilities?
- **Performance**: Will this impact system performance?
- **Maintainability**: Is the code easy to understand and modify?
- **Testing**: Are there adequate tests?
- **Documentation**: Is it properly documented?

## 🚀 Release Process

### Version Numbers

We use [Semantic Versioning](https://semver.org/):

- `MAJOR.MINOR.PATCH` (e.g., 1.2.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Workflow

1. Feature development happens on feature branches
2. Features are merged to `main` via PR
3. Release branches are created for preparing releases
4. Releases are tagged and deployed automatically

## 🤝 Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback  
- Help others learn and grow
- Celebrate diverse perspectives
- Report unacceptable behavior

### Communication

- **GitHub Issues**: Bug reports and feature requests
- **Pull Requests**: Code changes and discussions
- **Discussions**: General questions and ideas

### Getting Help

- Check the [documentation](docs/)
- Search [existing issues](https://github.com/your-org/another-doctor/issues)
- Ask in [GitHub Discussions](https://github.com/your-org/another-doctor/discussions)

## 🎉 Recognition

Contributors are recognized in:

- **README.md** contributor section
- **Release notes** for significant contributions
- **GitHub contributor graphs**

Thank you for contributing to Another Doctor! Your help makes a difference in connecting patients with the right medical specialists. 🏥