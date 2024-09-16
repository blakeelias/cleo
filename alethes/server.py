import hashlib
import time
from typing import Dict, Any
from fastapi import FastAPI, HTTPException

app = FastAPI()

# In-memory database to store hashes (in a real implementation, use a proper database)
db: Dict[str, Dict[str, Any]] = {}


def hash_data(data: str) -> str:
    """
    Generate a SHA-256 hash of the input data.

    Args:
        data (str): The input string to be hashed.

    Returns:
        str: The hexadecimal representation of the SHA-256 hash.
    """
    return hashlib.sha256(data.encode()).hexdigest()


@app.post("/submit")
async def submit_hash(x: str, m: str):
    """
    Submit a content hash and metadata to the server for timestamping and attestation.

    Args:
        x (str): The content hash generated by the client (X = Hash(D | T | M)).
        m (str): Additional metadata associated with the content.

    Returns:
        dict: A dictionary containing:
            - x_prime (str): The server-generated hash (X' = Hash(X | M)).
            - t_received (int): The server's timestamp of when the data was received.
            - attestation (str): The server's attestation (A = Hash(X' | K | T')).

    Raises:
        HTTPException: If there's an error processing the request.
    """
    t_received = int(time.time())
    x_prime = hash_data(f"{x}|{m}")

    # Store the hash
    db[x_prime] = {
        "x": x,
        "m": m,
        "t_received": t_received,
        "x_prime": x_prime
    }

    # Generate attestation
    k = "server_private_key"  # In a real implementation, use a secure private key
    attestation = hash_data(f"{x_prime}|{k}|{t_received}")

    return {
        "x_prime": x_prime,
        "t_received": t_received,
        "attestation": attestation
    }


@app.get("/verify/{x_prime}")
async def verify_hash(x_prime: str):
    """
    Verify a previously submitted hash and retrieve its associated data.

    Args:
        x_prime (str): The server-generated hash to verify.

    Returns:
        dict: A dictionary containing:
            - x (str): The original content hash submitted by the client.
            - m (str): The metadata associated with the content.
            - t_received (int): The server's timestamp of when the data was received.
            - x_prime (str): The server-generated hash.

    Raises:
        HTTPException: If the requested hash is not found in the database.
    """
    if x_prime not in db:
        raise HTTPException(status_code=404, detail="Hash not found")

    record = db[x_prime]
    return {
        "x": record["x"],
        "m": record["m"],
        "t_received": record["t_received"],
        "x_prime": record["x_prime"]
    }


@app.get("/hashes")
async def get_hashes():
    """
    Retrieve a list of all stored hashes. This endpoint is for demonstration purposes only.

    Returns:
        dict: A dictionary containing:
            - hashes (list): A list of all server-generated hashes (x_prime) stored in the database.
    """
    return {"hashes": list(db.keys())}
