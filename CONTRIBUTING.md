# Contributing to ChunkLab

First off, thank you for considering contributing to ChunkLab! It's people like you that make ChunkLab such a great tool.

## Code of Conduct

By participating in this project, you are expected to uphold our [Code of Conduct](CODE_OF_CONDUCT.md).

## How Can I Contribute?

### Reporting Bugs
- Use the **Bug Report** template when opening an issue.
- Describe the unexpected behavior and provide steps to reproduce.
- Include environment details (OS, Browser, Python version).

### Suggesting Enhancements
- Use the **Feature Request** template.
- Explain why this feature would be useful to the community.

## Development Setup

### Backend
1. Clone the repository.
2. `cd backend`
3. `python -m venv .venv`
4. Activate virtual environment.
5. `pip install -r requirements.txt`
6. `pip install ruff black pytest` (for development)

### Frontend
1. `cd frontend`
2. `npm install`
3. `npm run dev`

## Branching & Workflow

- **Branching Policy:**
  - `feat/feature-name` for new features.
  - `fix/bug-name` for bug fixes.
  - `docs/doc-update` for documentation changes.
- **Pull Requests:**
  - Target the `main` branch.
  - Ensure all tests pass.
  - Update documentation if necessary.

## Commit Guidelines

We follow **Conventional Commits**:
- `feat: add semantic chunking support`
- `fix: correct regex for multi-line headers`
- `docs: update quickstart instructions`

### Developer Certificate of Origin (DCO)

All commits must be signed off to certify that you have the right to submit the code. Use the `-s` flag:
```bash
git commit -s -m "feat: your commit message"
```

## Coding Standards

### Python
- Linter: `ruff`
- Formatter: `black`
- Style: Follow PEP 8.

### JavaScript/React
- Linter: `eslint`
- Formatter: `prettier`

## Testing Requirement

- New features must include unit tests.
- Run backend tests: `pytest`
- Run frontend tests: `npm test` (if applicable)

Thank you for your contributions!
