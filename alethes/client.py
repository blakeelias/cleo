import requests
import base64
import json
import time
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey

from alethes.common import hash_data

# Assuming the server is running on localhost:8000
BASE_URL = "https://90b61106-9a4b-40c4-8687-072ef2f03ed4-00-rc68466xvlwx.picard.replit.dev:3000"


def generate_content_hash(data: 'dict | str', metadata: 'dict | str', timestamp: int) -> str:
    """
    Generate a content hash from data, metadata, and timestamp.

    Args:
        data (dict | str): The image data or other content to be hashed.
        metadata (dict | str): Additional information about the content.
        timestamp (int): Unix timestamp representing when the hash was generated.

    Returns:
        str: A hexadecimal string representation of the SHA-256 hash.
    """
    # Convert data to string if it's not already
    if not isinstance(data, str):
        data = json.dumps(data)

    # Convert metadata to string if it's not already
    if not isinstance(metadata, str):
        metadata = json.dumps(metadata)

    # Concatenate all components
    content = f"{data}|{metadata}|{timestamp}"

    # Generate SHA-256 hash
    return hash_data(content)

def get_server_public_key() -> RSAPublicKey:
    """
    Fetch the server's public key.

    Returns:
        RSAPublicKey: The server's public key.
    """
    response = requests.get(f"{BASE_URL}/public_key")
    pem_public_key = response.json()["public_key"]
    return serialization.load_pem_public_key(pem_public_key.encode())

def submit_hash(content_hash: str, metadata: str) -> dict:
    """
    Submit a hash and metadata to the server.

    Args:
        content_hash (str): The content hash to be submitted.
        metadata (str): Additional metadata associated with the content.

    Returns:
        dict: The response from the server containing the attestation results.
    """
    response = requests.post(f"{BASE_URL}/submit", params={"x": content_hash, "m": metadata})
    return response.json()

def verify_signature(signature_b64: str, public_key: RSAPublicKey, x_prime: str) -> bool:
    """
    Verify the server's signature locally.

    Args:
        signature_b64 (str): The base64-encoded signature from the server.
        public_key (RSAPublicKey): The server's public key.
        x_prime (str): The content whose signature is to be verified.

    Returns:
        bool: True if the signature is valid, False otherwise.
    """
    try:
        signature = base64.b64decode(signature_b64)
        public_key.verify(
            signature,
            x_prime.encode(),
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
        return True
    except Exception as e:
        return False

def verify_hash(x_prime: str) -> 'dict | None':
    """
    Verify a previously submitted hash and retrieve its associated data.

    Args:
        x_prime (str): The server-generated hash to verify.

    Returns:
        dict | None: The data associated with the hash if verification is successful, None otherwise.
    """
    response = requests.get(f"{BASE_URL}/verify/{x_prime}")
    # Return associated data if verification is successful
    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_all_hashes() -> dict:
    """
    Fetch all stored hashes from the server.

    Returns:
        dict: A dictionary containing all stored hashes.
    """
    response = requests.get(f"{BASE_URL}/hashes")
    return response.json()


# Example usage
if __name__ == "__main__":
    # First, get the server's public key
    server_public_key = get_server_public_key()
    print("Server's public key retrieved.")

    # Hard-coded data and metadata
    data = {
        "image": "base64_encoded_image_data_here",
        "format": "jpeg"
    }
    metadata = {
        "user_id": "12345",
        "device": "iPhone 12",
        "location": "New York"
    }

    # Generate current timestamp
    timestamp = int(time.time())  # Unix timestamp (seconds since epoch)

    # Generate content hash
    content_hash = generate_content_hash(data, metadata, timestamp)

    # Submit the hash and metadata
    result = submit_hash(content_hash, metadata)
    print(f"Submitted hash. Result: {result}")

    # Verify the signature locally
    x_prime = result["x_prime"]
    signature_b64 = result["signature"]
    is_valid = verify_signature(signature_b64, server_public_key)
    print(f"Local signature verification result: {is_valid}")

    # Verify the hash and retrieve associated data
    verified_data = verify_hash(x_prime)
    if verified_data:
        print("Hash verification successful. Retrieved data:")
        print(verified_data)
        print(f"Original hash (x): {verified_data['x']}")
        print(f"Metadata (m): {verified_data['m']}")
        print(f"Timestamp (t): {verified_data['t_received']}")

        # Additional verification
        reconstructed_x_prime = hash_data(
            f"{verified_data['x']}|{verified_data['m']}")
        if reconstructed_x_prime == x_prime:
            print("Reconstructed x_prime matches the original.")
        else:
            print(
                "ERROR: Reconstructed x_prime does not match the original.")
            print(f"Reconstructed x_prime: {reconstructed_x_prime}")
            print(f"Original x_prime: {x_prime}")
            exit()
    else:
        print("ERROR: Hash verification failed or data not found.")
        exit()

    # Try to verify a non-existent hash
    non_existent_x_prime = "This_hash_does_not_exist"
    non_existent_data = verify_hash(non_existent_x_prime)
    if non_existent_data is None:
        print(
            f"As expected, no data found for non-existent hash: {non_existent_x_prime}"
        )
    else:
        print(
            f"ERROR: Data found for supposedly non-existent hash: {non_existent_x_prime}"
        )
        exit()

    # Fetch all stored hashes
    # For debugging / demonstration purposes only
    all_hashes = get_all_hashes()
    print(f"All stored hashes: {all_hashes}")
