import json
import sys

def verify_data_product_assertion(payload: dict) -> tuple[bool, list[str]]:
    errors = []

    # 1. Validar Codificación Semántica (ISO 8000-110)
    uri = payload.get("iso8000:semanticEncodingURI", "")
    if not uri.startswith("https://"):
        errors.append("ISO 8000-110 Violation: Missing valid HTTPS semantic encoding URI.")

    # 2. Validar Proveniencia y Custodia (ISO 8000-120)
    attribution = payload.get("prov:wasAttributedTo", {})
    if not attribution.get("identifier", "").startswith("did:"):
        errors.append("ISO 8000-120 Violation: Source Data Owner must use a valid W3C DID.")

    # 3. Validar Umbrales de Calidad (ISO 8000-130/140)
    metrics = payload.get("iso8000:qualityMetrics", {})
    if metrics.get("iso8000:syntacticAccuracy", 0) < 0.99:
        errors.append("ISO 8000-130 Violation: Syntactic accuracy below 0.99 threshold.")
    if metrics.get("iso8000:completenessScore", 0) < 1.0:
        errors.append("ISO 8000-140 Violation: Master data completeness must equal 1.0.")

    # 4. Validar Política Cero PII (Privacy-by-Design)
    if metrics.get("fdagm:piiExposureLevel") != "ZERO_RAW_PII":
        errors.append("Privacy Violation: Central gateway rejects payloads containing raw PII.")

    # 5. Validar Prueba Criptográfica (Integridad de Auditoría)
    proof = payload.get("fdagm:cryptographicProof", {})
    if proof.get("hashAlgorithm") != "SHA-256" or len(proof.get("merkleRootHash", "")) != 64:
        errors.append("Integrity Violation: Invalid SHA-256 Merkle root hash.")

    return (len(errors) == 0, errors)

if __name__ == "__main__":
    with open("schemas/quality-assertion.jsonld", "r", encoding="utf-8") as f:
        sample_assertion = json.load(f)

    is_valid, validation_errors = verify_data_product_assertion(sample_assertion)
    if is_valid:
        print("STATUS: VERIFIED | Assertion passed ISO-as-Code Quality Gate.")
        sys.exit(0)
    else:
        print("STATUS: REJECTED")
        for err in validation_errors:
            print(f" - {err}")
        sys.exit(1)
