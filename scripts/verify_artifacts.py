"""Verification script for Veyra ML artifacts, Git-LFS detection, and cryptographic provenance."""
import hashlib
import json
import sys
from pathlib import Path

GIT_LFS_HEADER_PREFIX = b"version https://git-lfs.github.com/spec/v1"

def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().lower()

def is_git_lfs_pointer(path: Path) -> bool:
    if not path.is_file():
        return False
    if path.stat().st_size > 1024:
        return False
    try:
        content = path.read_bytes()
        return content.startswith(GIT_LFS_HEADER_PREFIX)
    except Exception:
        return False

def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    manifest_path = repo_root / "models" / "v3" / "artifact_manifest.json"
    
    print("=" * 65)
    print("Veyra ML Artifact Chain & SHA-256 Provenance Verification")
    print("=" * 65)
    
    if not manifest_path.is_file():
        print(f"[FAIL] Manifest file missing: {manifest_path}")
        return 1
    
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"[FAIL] Could not parse manifest JSON: {exc}")
        return 1
    
    artifacts = manifest.get("artifacts", {})
    all_passed = True
    
    for key, spec in artifacts.items():
        rel_path = spec["path"]
        expected_sha = spec["sha256"]
        file_path = repo_root / rel_path
        
        print(f"\nVerifying artifact [{key}]: {rel_path}...")
        
        if not file_path.is_file():
            print(f"  [FAIL] File does not exist: {file_path}")
            all_passed = False
            continue
        
        # Git LFS stub check
        if is_git_lfs_pointer(file_path):
            print(f"  [FAIL] Detected Git-LFS pointer stub instead of binary weights!")
            print(f"         File size: {file_path.stat().st_size} bytes.")
            print(f"         Action required: Run 'git lfs pull' to fetch actual weights.")
            all_passed = False
            continue
        
        actual_sha = compute_sha256(file_path)
        actual_size = file_path.stat().st_size
        
        if actual_sha != expected_sha:
            print(f"  [FAIL] SHA-256 checksum mismatch!")
            print(f"         Expected: {expected_sha}")
            print(f"         Actual:   {actual_sha}")
            all_passed = False
            continue
        
        print(f"  [PASS] SHA-256 matched: {actual_sha}")
        print(f"  [PASS] File size: {actual_size:,} bytes")
        
        # Additional checks for feature schema
        if key == "features":
            try:
                features = json.loads(file_path.read_text(encoding="utf-8"))
                if len(features) != spec.get("feature_count", 50):
                    print(f"  [FAIL] Feature count mismatch: {len(features)} != {spec.get('feature_count', 50)}")
                    all_passed = False
                else:
                    print(f"  [PASS] Feature count verified: {len(features)} canonical features.")
            except Exception as exc:
                print(f"  [FAIL] Could not parse feature schema: {exc}")
                all_passed = False

    # Try unpickling the model and calibrator
    print("\n[Sanity] Verifying model and calibrator loadability with joblib...")
    try:
        import joblib
        model_path = repo_root / artifacts["model"]["path"]
        calibrator_path = repo_root / artifacts["calibrator"]["path"]
        
        model = joblib.load(model_path)
        print(f"  [PASS] Model loaded: {type(model).__name__}")
        
        calibrator = joblib.load(calibrator_path)
        print(f"  [PASS] Calibrator loaded: {type(calibrator).__name__}")
    except Exception as exc:
        print(f"  [FAIL] Joblib loading failed: {exc}")
        all_passed = False

    print("\n" + "=" * 65)
    if all_passed:
        print("All ML artifact integrity and provenance checks PASSED.")
        print("=" * 65)
        return 0
    else:
        print("ML artifact verification FAILED. Please review errors above.")
        print("=" * 65)
        return 1

if __name__ == "__main__":
    sys.exit(main())
