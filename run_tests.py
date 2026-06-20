"""Run tests and display results."""
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/test_error_handling.py", "-v", "--tb=short"],
    capture_output=True,
    text=True,
    cwd=r"C:\MyProject\api_python"
)

print("STDOUT:")
print(result.stdout)
print("\nSTDERR:")
print(result.stderr)
print(f"\nReturn code: {result.returncode}")