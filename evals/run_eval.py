"""Small eval runner for the Agent demo.

The dataset checks whether each prompt triggers the expected tool, contains the
expected answer text, and produces the expected handoff decision.
"""

import json
from datetime import datetime
from pathlib import Path

from app.db.crud import add_eval_result, create_eval_run
from app.rag.ingest import ingest_text
from app.rag.store import list_documents
from app.schemas.chat import ChatRequest
from app.services.chat_service import handle_chat


def seed_sample_document() -> None:
    """Ensure the retrieval eval has at least one sample document to search."""
    if any(item["filename"] == "agent_intro.txt" for item in list_documents()):
        return
    sample = Path("sample_docs/agent_intro.txt")
    if sample.exists():
        ingest_text(filename=sample.name, text=sample.read_text(encoding="utf-8"))


def main() -> None:
    """Run eval rows, persist results, and write a JSON report."""
    seed_sample_document()
    dataset_path = Path(__file__).with_name("dataset.jsonl")
    rows = [json.loads(line) for line in dataset_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    results = []

    for row in rows:
        # Reuse one eval session so history behavior is exercised too.
        response = handle_chat(ChatRequest(message=row["message"], session_id="eval-session"))
        tools = sorted({tool.tool_name for tool in response.used_tools})
        contains_ok = row["expected_contains"].lower() in response.answer.lower()
        tool_ok = row["expected_tool"] in tools
        handoff_ok = response.need_human == row.get("expected_need_human", False)
        ok = contains_ok and tool_ok and handoff_ok
        results.append(
            {
                "message": row["message"],
                "ok": ok,
                "tools": tools,
                "contains_ok": contains_ok,
                "tool_ok": tool_ok,
                "handoff_ok": handoff_ok,
                "need_human": response.need_human,
            }
        )
        print(json.dumps(results[-1], ensure_ascii=False))

    passed = sum(1 for item in results if item["ok"])
    run_id = create_eval_run(name=f"eval-{datetime.now().isoformat(timespec='seconds')}", total=len(rows), passed=passed)
    for row, item in zip(rows, results, strict=True):
        add_eval_result(
            eval_run_id=run_id,
            question=row["message"],
            expected_tool=row["expected_tool"],
            actual_tools=item["tools"],
            passed=item["ok"],
            notes=json.dumps(item, ensure_ascii=False),
        )

    report = {
        # These aggregate numbers are intentionally simple for easy inspection.
        "eval_run_id": run_id,
        "total": len(results),
        "passed": passed,
        "pass_rate": round(passed / len(results), 4) if results else 0,
        "tool_accuracy": round(sum(1 for item in results if item["tool_ok"]) / len(results), 4) if results else 0,
        "answer_contains_accuracy": round(sum(1 for item in results if item["contains_ok"]) / len(results), 4)
        if results
        else 0,
        "handoff_accuracy": round(sum(1 for item in results if item["handoff_ok"]) / len(results), 4) if results else 0,
        "results": results,
    }
    report_path = Path(__file__).with_name("eval_report.json")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"passed={passed}/{len(results)}")
    print(f"report={report_path}")


if __name__ == "__main__":
    main()
