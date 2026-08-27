import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVALS_DIR = ROOT / "evals"


def test_all_evals_have_name_prompt_check():
    json_files = list(EVALS_DIR.glob("*.json"))
    assert json_files, "No eval JSON files found"
    for path in json_files:
        data = json.loads(path.read_text())
        for field in ("name", "prompt", "check"):
            assert field in data, f"{path} missing {field}"
        check_path = ROOT / data["check"]
        assert check_path.is_file(), f"Check script not found: {check_path}"
        assert check_path.stat().st_mode & 0o111, f"Check script is not executable: {check_path}"