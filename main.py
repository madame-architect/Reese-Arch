"""Simple example script with explanatory comments.

This module demonstrates a small utility function and prints a greeting.
"""

from __future__ import annotations


def add(a: float, b: float) -> float:
    """Add two numbers and return the result.

    Parameters
    ----------
    a: float
        First operand.
    b: float
        Second operand.
    """
    return a + b


if __name__ == "__main__":
    # Demonstrate the add function and print a greeting
    result = add(1, 2)
    print(f"Hello from Reese-Arch! 1 + 2 = {result}")
