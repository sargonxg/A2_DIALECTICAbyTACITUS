"""
Admin Key Generator — Create and store initial admin API key.

Generates a cryptographically secure random key, hashes with SHA-256,
inserts into APIKeys table, and prints the key (one-time display).

Store the key securely! It cannot be retrieved after creation.

TODO: Implement in Prompt 10
"""
import secrets
import hashlib

def main():
    key = secrets.token_urlsafe(32)
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    print(f"Generated admin key: {key}")
    print(f"Key hash (stored in DB): {key_hash}")
    print("TODO: Insert into Spanner APIKeys table")

if __name__ == "__main__":
    main()
