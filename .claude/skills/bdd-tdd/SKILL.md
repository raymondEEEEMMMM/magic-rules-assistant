---
name: bdd-tdd
description: BDD/TDD development methodology - test frameworks (pytest), behavior-driven development with Gherkin, TDD cycle (red-green-refactor), and test organization patterns for this MTG project.
---

## Core Philosophy

**TDD (Test-Driven Development)**: Write tests BEFORE code. Follow the cycle: Red → Green → Refactor.

**BDD (Behavior-Driven Development)**: Express requirements as executable specifications in Gherkin (Given-When-Then).

## TDD Cycle

```
1. Red:     Write a failing test for the feature you want
2. Green:   Write minimum code to make the test pass
3. Refactor:Improve code while keeping tests green
4. Repeat
```

## Gherkin Syntax (for BDD specifications)

```gherkin
Feature: Card Search
  Scenario: Search cards by Chinese name
    Given The card database is loaded
    When I search for "黑莲花"
    Then I should get "Black Lotus" as the result
    And The card type should be "Legendary Artifact Creature"
```

## Test Organization (this project)

```
tests/
├── conftest.py           # pytest fixtures & configuration
├── unit/                 # Unit tests (fast, isolated)
│   └── test_*.py
├── integration/          # Integration tests (with real services)
│   └── test_*.py
├── cloud/                # Cloud function tests
├── sample/               # Sample data for tests
└── utils/                # Test utilities
```

## Pytest Fixtures (this project)

```python
@pytest.fixture
def mock_db():
    """Mock database for unit tests"""
    with patch('routes.RuleDatabase') as mock:
        yield mock.return_value

@pytest.fixture
def client(mock_db, mock_rule_service):
    """FastAPI TestClient fixture"""
    from fastapi.testclient import TestClient
    from backend.routes import app
    yield TestClient(app)
```

## Running Tests

```bash
# All tests
pytest tests/

# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Single test file
pytest tests/unit/test_0_routes.py -v

# With coverage
pytest tests/unit/ --cov=backend --cov-report=term-missing
```

## TDD Rules

1. **Never write production code without a failing test first**
2. **Tests must be fast** (unit tests < 100ms each)
3. **Test one thing per test function**
4. **Use descriptive test names**: `test_search_returns_card_when_exact_name_match`
5. **Arrange-Act-Assert pattern**:
   ```python
   def test_search_returns_card_by_name():
       # Arrange
       db = MockCardDatabase()

       # Act
       result = db.search("黑莲花")

       # Assert
       assert result.name == "Black Lotus"
   ```

## BDD Implementation

Use `pytest-bdd` for BDD-style tests:

```bash
pip install pytest-bdd
```

Feature files (`.feature`) go in `tests/bdd/`:

```gherkin
# tests/bdd/card_search.feature
Feature: Card Search API
  Scenario: Search with Chinese name returns card details
    Given the card service is available
    When I call GET /api/card?n=黑莲花
    Then the response should contain card_name "Black Lotus"
    And the response should contain mana_cost "0"
```

Step definitions in `tests/bdd/steps/`:
```python
# tests/bdd/steps/card_steps.py
from pytest_bdd import given, when, then

@given("the card service is available")
def card_service():
    return CardService()

@when("I call GET /api/card?n=黑莲花")
def search_card(card_service):
    return card_service.search(name="黑莲花")

@then("the response should contain card_name {expected}")
def verify_card_name(response, expected):
    assert response["card_name"] == expected
```

## Test Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Unit | `test_<module>_<scenario>` | `test_routes_search_returns_404` |
| Integration | `test_<service>_<flow>` | `test_card_service_search_by_name` |
| BDD | Feature-driven | Given-When-Then in `.feature` |

## Mocking Guidelines

```python
# Use patch for external dependencies
@patch('backend.services.card_service.ScryfallAPI')
def test_search_mock_scryfall(mock_scryfall):
    mock_scryfall.return_value.search.return_value = {...}
    ...

# For database tests, use conftest.py fixtures
@pytest.fixture
def seeded_db():
    """Database with test data"""
    db = TestDatabase()
    db.seed(Card(name="Black Lotus", ...))
    return db
```

## Continuous Testing

Run tests automatically on file changes:
```bash
pytest tests/unit/ -w
# or
ptw  # pytest-watch
```