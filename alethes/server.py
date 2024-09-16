import time
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.routing import APIRoute
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
import base64

from alethes.common import hash_data

app = FastAPI()

# Generate a key pair for the server (in a real-world scenario, you'd store these securely)
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()

# Serialize the public key to PEM format
pem_public_key = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo)

# In-memory database to store hashes (in a real implementation, use a proper database)
db: Dict[str, Dict[str, Any]] = {}


@app.post("/submit")
async def submit_hash(x: str, m: str, store=True, attest=True):
    """
    Submit a content hash and metadata to the server for timestamping and attestation.

    This endpoint allows clients to submit a content hash and associated metadata
    to be timestamped and attested by the server.

    Args:
        x (str): The content hash generated by the client (X = Hash(D | T | M)).
        m (str): Additional metadata associated with the content.
        store (bool, optional): Whether to store the submitted data in the database. Defaults to True.
        attest (bool, optional): Whether to return attestation of the submitted data. Defaults to True.

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

    if store:
        # Store the hash
        db[x_prime] = {
            "x": x,
            "m": m,
            "t_received": t_received,
            "x_prime": x_prime
        }

        return 'Received'

    if attest:
        # Sign the data
        signature = private_key.sign(
            x_prime.encode(),
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())

        # Encode the signature as base64 for easy transmission
        signature_b64 = base64.b64encode(signature).decode()

        return {
            "x_prime": x_prime,
            "t_received": t_received,
            "signature": signature_b64
        }


@app.get("/verify/{x_prime}")
async def verify_hash(x_prime: str):
    """
    Verify a previously submitted hash and retrieve its associated data.

    This endpoint allows clients to verify the existence and retrieve the details
    of a previously submitted hash.

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


@app.get("/public_key")
async def get_public_key():
    """
    Retrieve the server's public key.

    This endpoint allows clients to fetch the server's public key,
    which can be used to verify signatures.
    """
    return {"public_key": pem_public_key.decode()}


@app.get("/hashes")
async def get_hashes():
    """
    Retrieve a list of all stored hashes.
    
    This endpoint returns a list of all server-generated hashes (x_prime) stored in the database.
    It's primarily for demonstration purposes.

    Returns:
        dict: A dictionary containing:
            - hashes (list): A list of all server-generated hashes (x_prime) stored in the database.
    """
    return {"hashes": list(db.keys())}


@app.get("/")
async def root():
    """
    List all available routes in the application.

    Returns:
        dict: A dictionary containing:
            - routes (List[dict]): A list of dictionaries, each containing:
                - path (str): The path of the route.
                - methods (List[str]): HTTP methods supported by the route.
                - name (str): The name of the route (if any).
                - summary (str): A brief summary of the route (if provided in docstring).
    """
    routes: List[dict] = []

    for route in app.routes:
        if isinstance(route, APIRoute):
            routes.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": route.name,
                "summary": route.summary or route.description.split('\n')[0]
                or "No summary provided"
            })

    return {"routes": routes}
