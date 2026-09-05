"""
Pytest configuration for stroke-neuroimaging-agent test suite.
Sets required environment variables for secure test execution.
"""
import os


def pytest_configure(config):
    """Set required environment variables before test collection."""
    os.environ.setdefault("AUDIT_SECRET_KEY", "test-audit-secret-key-for-testing-only-do-not-use-in-production-2026")
