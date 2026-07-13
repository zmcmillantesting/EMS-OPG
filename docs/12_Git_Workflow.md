# Git Workflow Guide

## Overview

This document outlines the Git workflow and branching strategy used in the EMS-OPG project. Following a structured branching model helps maintain code quality, ensures organized development, and simplifies the release process.

## Workflow Process

```
main
  ↓
develop
  ↓
feature
  ↓
pull request
  ↓
review
  ↓
merge
  ↓
release
```

---

## Branch Strategy

The project uses a hierarchical branch structure based on Git Flow principles:

```
main
│
├── develop
│
├── feature/
│   ├── feature/database-design
│   ├── feature/sqlalchemy
│   ├── feature/login
│   ├── feature/inventory
│   ├── feature/settings
│   ├── feature/reports
│   └── feature/logging
│
├── bugfix/
│   ├── bugfix/login-timeout
│   └── bugfix/report-crash
│
├── hotfix/
│   └── hotfix/v1.0.1-crash
│
├── release/
│   └── release/v1.0.0
│
└── docs/
    ├── docs/database-design
    └── docs/user-manual
```

### Branch Types

#### **main** (Production)
- Production-ready code only
- Stable releases
- Tagged with version numbers

#### **develop** (Integration)
- Development and testing branch
- Integration point for features
- Basis for new feature branches

#### **feature/** (Development)
- New features and enhancements
- Branched from: `develop`
- Merged back to: `develop` via Pull Request
- Examples:
  - `feature/database-design`
  - `feature/login`
  - `feature/inventory`

#### **bugfix/** (Bug Fixes)
- Non-critical bug fixes
- Branched from: `develop`
- Merged back to: `develop` via Pull Request
- Examples:
  - `bugfix/login-timeout`
  - `bugfix/report-crash`

#### **hotfix/** (Urgent Fixes)
- Critical production bugs requiring immediate fix
- Branched from: `main`
- Merged to: both `main` and `develop`
- Examples:
  - `hotfix/v1.0.1-crash`

#### **release/** (Release Preparation)
- Release preparation and version bumps
- Branched from: `develop`
- Merged to: `main` and back to `develop`
- Examples:
  - `release/v1.0.0`

#### **docs/** (Documentation)
- Documentation updates
- Branched from: `develop`
- Merged back to: `develop` via Pull Request
- Examples:
  - `docs/database-design`
  - `docs/user-manual`

---

## Best Practices

- Keep branch names descriptive and lowercase
- Use hyphens to separate words in branch names
- Delete merged branches to keep the repository clean
- Write meaningful commit messages
- Create Pull Requests for code review before merging
- Ensure all CI/CD checks pass before merging