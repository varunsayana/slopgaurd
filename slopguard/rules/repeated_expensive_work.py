from typing import Optional,  List, Any
from slopguard.models import Finding, Severity, Confidence, Category
from slopguard.rules.base import BaseRule
from slopguard.parsers.base import BaseParser
import re


class RepeatedExpensiveWorkRule(BaseRule):
    def __init__(self, config_options: Optional[dict] = None):
        super().__init__("repeated_expensive_work", config_options)

    def evaluate(
        self, file_path: str, code: str, parsed_ast: Any, parser: BaseParser
    ) -> List[Finding]:
        findings = []
        inside_loop = False
        for i, line in enumerate(code.splitlines()):
            if re.match(r"^\s*(for|while)\s+", line):
                inside_loop = True
                i + 1
            elif inside_loop and re.search(
                r"\s*(requests\.get|Query\.execute|db\.query)", line
            ):
                findings.append(
                    Finding(
                        rule_id=self.rule_id,
                        title="Repeated Expensive Work",
                        severity=Severity.HIGH,
                        confidence=Confidence.MEDIUM,
                        file_path=file_path,
                        line_number=i + 1,
                        short_explanation="Performant-critical external call found inside a loop.",
                        why_it_matters="Creates an N+1 performance bottleneck.",
                        suggested_remediation="Batch the query or hoist the request outside the loop.",
                        categories=[Category.PERFORMANCE_RISK],
                    )
                )
                inside_loop = False  # Reset to avoid spam
            elif inside_loop and not line.startswith(" ") and not line.startswith("\t"):
                inside_loop = False
        return findings
