import time
import json
import uuid

def validate_iso8000_record(record):
    # Regla 1: Completitud sintáctica (campos obligatorios)
    required_fields = ["@context", "@type", "assetId", "timestamp", "payloadHash"]
    if not all(field in record and record[field] for field in required_fields):
        return False, 0.0
    
    # Regla 2: Conformidad semántica y cero exposición de PII
    if record.get("piiExposed", True) is not False:
        return False, 0.4
    
    # Regla 3: Umbral de calidad ISO 8000-110
    score = record.get("qualityScore", 0.0)
    return (score >= 0.95), score

def run_benchmark(batch_sizes=[100, 1000, 10000]):
    print(f"{'Batch Size':<12} | {'Total Time (ms)':<18} | {'Mean Latency/Rec (ms)':<22}")
    print("-" * 58)
    for size in batch_sizes:
        dataset = [
            {
                "@context": "https://w3id.org/fdagm/v2/quality-assertion.jsonld",
                "@type": "DataQualityAssertion",
                "assetId": f"urn:fdagm:node-pe:{uuid.uuid4()}",
                "timestamp": "2026-11-12T15:30:00Z",
                "payloadHash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "piiExposed": False,
                "qualityScore": 0.99
            }
            for _ in range(size)
        ]
        
        start_time = time.perf_counter()
        for item in dataset:
            validate_iso8000_record(item)
        end_time = time.perf_counter()
        
        total_ms = (end_time - start_time) * 1000
        mean_ms = total_ms / size
        print(f"{size:<12} | {total_ms:<18.3f} | {mean_ms:<22.5f}")

if __name__ == "__main__":
    run_benchmark()
