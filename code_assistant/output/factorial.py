n
def factorial(n):
    """
    Calculate the factorial of a given number recursively.

    Parameters:
    n (int): A non-negative integer for which the factorial is to be calculated.

    Returns:
    int: The factorial of 'n'.

    Raises:
    ValueError: If 'n' is not a non-negative integer.
    """
    # Input validation
    if not isinstance(n, int):
        raise ValueError("The input must be an integer.")
    if n < 0:
        raise ValueError("Factorial is not defined for negative integers.")

    # Base case: 0! = 1
    if n == 0:
        return 1

    # Recursive case: n! = n * (n-1)!
    return n * factorial(n-1)

# Example Usage
if __name__ == "__main__":
    try:
        number = 5
        print(f"The factorial of {number} is: {factorial(number)}")
    except ValueError as error:
        print(f"Error: {error}")