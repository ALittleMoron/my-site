#!/usr/bin/env python3
from __future__ import annotations

import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID


def main() -> None:
    issuer_certificate_path, issuer_key_path, certificate_path, key_path = map(
        Path,
        sys.argv[1:5],
    )
    certificate_name = sys.argv[5]
    validity = sys.argv[6]
    issuer_certificate = x509.load_pem_x509_certificate(issuer_certificate_path.read_bytes())
    issuer_key = serialization.load_pem_private_key(
        issuer_key_path.read_bytes(),
        password=None,
    )
    key = ec.generate_private_key(ec.SECP256R1())
    now = datetime.now(UTC)
    not_valid_before = now - timedelta(days=2) if validity == "expired" else now - timedelta(minutes=1)
    not_valid_after = now - timedelta(days=1) if validity == "expired" else now + timedelta(days=1)
    certificate = (
        x509.CertificateBuilder()
        .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, certificate_name)]))
        .issuer_name(issuer_certificate.subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(not_valid_before)
        .not_valid_after(not_valid_after)
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=None,
                decipher_only=None,
            ),
            critical=True,
        )
        .add_extension(
            x509.ExtendedKeyUsage([ExtendedKeyUsageOID.CLIENT_AUTH]),
            critical=False,
        )
        .sign(issuer_key, hashes.SHA256())
    )
    key_path.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ),
    )
    certificate_path.write_bytes(certificate.public_bytes(serialization.Encoding.PEM))


if __name__ == "__main__":
    main()
