---
name: binary-credential-format-boundary
description: Audit and repair readers for fixed-length binary credentials and their text encodings without mutating raw bytes. Use when code loads Ed25519/X25519 keys, nonces, digests, MAC keys, signatures, tokens, or other opaque bytes from files or environment values; when `.strip()`, decoding, newline handling, or format auto-detection occurs before length/type validation; or when cryptographic tests fail intermittently for otherwise valid generated material.
---

# Binary Credential Format Boundary

Preserve opaque binary values byte-for-byte while supporting explicitly defined text encodings through a separate parsing branch. Treat a flaky cryptographic verification as a possible ingestion bug before changing the cryptographic primitive.

## Diagnose

1. Reproduce the failure and capture only exception types, lengths, and hashes; never print credential bytes.
2. Verify the primitive independently with an in-memory generate/sign/verify or encrypt/decrypt control.
3. Trace the exact bytes from serialization through file/environment ingestion to the primitive.
4. Look for pre-validation mutations: `.strip()`, `.splitlines()`, Unicode decode/encode, newline normalization, NUL termination, case conversion, or permissive Base64 decoding.
5. Compare interpreter and library versions only after the byte path is proven unchanged.

## Parse Without Ambiguity

For a contract that accepts either a fixed-length raw value or Base64 text:

```python
raw = path.read_bytes()
if len(raw) == EXPECTED_RAW_LENGTH:
    value = raw
else:
    value = base64.b64decode(raw.strip(), validate=True)
    if len(value) != EXPECTED_RAW_LENGTH:
        raise ValueError("invalid credential length")
```

Apply text cleanup only inside the text-encoding branch. Do not call `.strip()` before checking the raw representation: bytes such as `0x09`, `0x0a`, `0x0b`, `0x0c`, `0x0d`, and `0x20` are valid opaque octets and may occur at either boundary.

Prefer an explicit format option or distinct file extension when the accepted encodings can have overlapping lengths. Use official PEM/DER/JWK loaders for those formats instead of inventing detection logic. Reject unknown, ambiguous, malformed, oversized, or non-canonical input fail-closed.

## Test First

Add deterministic regressions before changing the reader:

- A raw value of the exact required length whose first byte is an ASCII whitespace octet.
- A raw value whose final byte is an ASCII whitespace octet.
- Raw values containing NUL and non-UTF-8 octets.
- Valid Base64 text with the contractually allowed line ending.
- Invalid Base64, decoded wrong length, ambiguous representation, and extra binary bytes.
- An end-to-end primitive check using the loaded value.

Also repeat any formerly random positive test enough times to show the intermittent path is gone. Do not replace a random test with only a deterministic fixture; retain both coverage types.

## Reject These Fixes

- Retrying key generation until the serialized bytes avoid whitespace.
- Stripping, decoding, or normalizing all input before format detection.
- Catching the parse error and silently generating or substituting a new credential.
- Relaxing Base64 validation or accepting arbitrary decoded lengths.
- Logging raw keys, signatures, tokens, or decoded credential material.
- Treating a probabilistic pass as proof that the boundary is correct.

## Completion Standard

- The deterministic boundary-octet regression fails on the old implementation and passes on the fix.
- Raw fixed-length input is returned byte-for-byte unchanged.
- Text input is normalized only within its explicit parser and is strictly validated after decoding.
- End-to-end cryptographic verification passes, including repeated formerly flaky runs.
- Negative and malformed inputs still fail closed.
- The full relevant test suite and static/compile checks pass.
- No credential value appears in logs, reports, fixtures intended for publication, or error messages.
