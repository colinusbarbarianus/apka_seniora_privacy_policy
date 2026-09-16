#!/usr/bin/env python3
"""
Signs the published threat-catalog JSON files with the project's Ed25519
signing key, so the app can verify it downloaded genuine content and not
something tampered with in transit or by a compromised host.

Usage:
    export THREATS_SIGNING_KEY_B64="<private key, base64, 32 raw bytes>"
    python3 scripts/sign_threats.py

Run this from the repo root after editing any file under threats/*.json.
Commit both the updated .json file AND its regenerated .json.sig file —
the app rejects a JSON file whose signature does not match.

The private key must NEVER be committed to this repo (it's public). Keep
it in a password manager or local keychain and pass it via the
THREATS_SIGNING_KEY_B64 environment variable only.
"""
import base64
import glob
import os
import sys

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

KEY_ENV_VAR = "THREATS_SIGNING_KEY_B64"


def main() -> int:
    key_b64 = os.environ.get(KEY_ENV_VAR)
    if not key_b64:
        print(f"error: set {KEY_ENV_VAR} (base64 private key) before running this script", file=sys.stderr)
        return 1

    try:
        priv = Ed25519PrivateKey.from_private_bytes(base64.b64decode(key_b64))
    except Exception as exc:  # noqa: BLE001 - want a clear message for any bad-key shape
        print(f"error: could not load private key from {KEY_ENV_VAR}: {exc}", file=sys.stderr)
        return 1

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    threats_dir = os.path.join(repo_root, "threats")
    json_files = sorted(glob.glob(os.path.join(threats_dir, "*.json")))

    if not json_files:
        print(f"error: no .json files found under {threats_dir}", file=sys.stderr)
        return 1

    for path in json_files:
        with open(path, "rb") as f:
            message = f.read()
        signature = priv.sign(message)
        sig_path = path + ".sig"
        with open(sig_path, "w", encoding="ascii") as f:
            f.write(base64.b64encode(signature).decode("ascii"))
        print(f"signed: {os.path.relpath(path, repo_root)} -> {os.path.relpath(sig_path, repo_root)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
