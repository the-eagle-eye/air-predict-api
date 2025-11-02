"""
Pytest configuration and shared fixtures
"""
import pytest
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))


def pytest_configure(config):
    """Pytest configuration hook"""
    print("\n" + "="*60)
    print("🧪 CR310 Datalogger API - Test Suite")
    print("="*60)


def pytest_sessionfinish(session, exitstatus):
    """Pytest session finish hook"""
    print("\n" + "="*60)
    if exitstatus == 0:
        print("✅ All tests passed!")
    else:
        print(f"❌ Some tests failed (exit status: {exitstatus})")
    print("="*60 + "\n")

