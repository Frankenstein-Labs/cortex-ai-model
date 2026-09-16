import json
from pathlib import Path
REQUIRED = {"instruction", "context", "input", "output", "tests", "result"}
STATUSES = {"candidate", "reviewed", "approved", "rejected"}

def validate_jsonl(path: Path) -> list[str]:
    errors=[]
    for n, line in enumerate(path.read_text().splitlines(), 1):
        try: item=json.loads(line)
        except json.JSONDecodeError as exc: errors.append(f"line {n}: invalid JSON ({exc.msg})"); continue
        missing=REQUIRED-set(item)
        if missing: errors.append(f"line {n}: missing {sorted(missing)}")
        if item.get("result") not in {"passed", "failed"}: errors.append(f"line {n}: result must be passed or failed")
        if item.get("status", "candidate") not in STATUSES: errors.append(f"line {n}: invalid status")
    return errors

def build_dataset(input_path: Path, output_path: Path) -> int:
    rows=[]
    for line in input_path.read_text().splitlines():
        item=json.loads(line)
        if item.get("result") == "passed" and item.get("status") in {"reviewed", "approved"}: rows.append(item)
    output_path.write_text("".join(json.dumps(row, ensure_ascii=False)+"\n" for row in rows))
    return len(rows)
