import hashlib


def hash_data(data: str) -> str:
    """
    Generate a SHA-256 hash of the input data.

    Args:
        data (str): The input string to be hashed.

    Returns:
        str: The hexadecimal representation of the SHA-256 hash.
    """
    return hashlib.sha256(data.encode()).hexdigest()
