"""
Tests package for unit and integration tests

PACKAGE PURPOSE:
    Contains all test files for ensuring code quality and correctness.
    Uses pytest framework for testing.

TEST CATEGORIES:
    - Unit Tests: Test individual functions/classes
    - Integration Tests: Test component interactions
    - End-to-End Tests: Test complete workflows
    - Performance Tests: Test speed and resource usage

KEY CONCEPTS:
    - Test Coverage: % of code tested (target: >80%)
    - Assertions: Verify expected behavior
    - Fixtures: Reusable test data and setup
    - Mocking: Simulate external dependencies
    - Parametrized Tests: Test multiple inputs

TEST STRUCTURE:
    tests/
        test_data_pipeline.py - Data loading and preprocessing tests
        test_validators.py - Validation pipeline tests
        test_models.py - Model architecture tests
        monitoring/
            test_metrics.py - Metrics collection tests
            test_alerts.py - Alert system tests

RUNNING TESTS:
    # Run all tests
    pytest tests/
    
    # Run specific test file
    pytest tests/test_validators.py
    
    # Run with coverage
    pytest --cov=src tests/
    
    # Run verbose
    pytest -v tests/

USAGE:
    # Example test
    def test_image_validator():
        validator = ImageValidator()
        is_valid, results = validator.validate('test_xray.jpg')
        assert is_valid == True
        assert results['quality_score'] > 60
"""

__all__ = []
