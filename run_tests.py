#!/usr/bin/env python3
"""Test runner script with different test configurations."""
import subprocess
import sys
import argparse


def run_command(cmd):
    """Run a command and return the exit code."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Run tests with different configurations")
    parser.add_argument("--type", choices=["unit", "integration", "all"], default="all",
                       help="Type of tests to run")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--fast", action="store_true", help="Skip slow tests")
    
    args = parser.parse_args()
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add test type
    if args.type == "unit":
        cmd.extend(["tests/test_api", "tests/test_clients", "tests/test_db", 
                   "tests/test_etl", "tests/test_ml"])
    elif args.type == "integration":
        cmd.extend(["tests/test_integration"])
    else:  # all
        cmd.extend(["tests/"])
    
    # Add coverage if requested
    if args.coverage:
        cmd.extend(["--cov=src", "--cov-report=html", "--cov-report=term"])
    
    # Add verbose if requested
    if args.verbose:
        cmd.append("-v")
    
    # Skip slow tests if requested
    if args.fast:
        cmd.extend(["-m", "not slow"])
    
    # Run the tests
    exit_code = run_command(cmd)
    
    if exit_code == 0:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
