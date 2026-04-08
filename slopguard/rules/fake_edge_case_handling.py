from typing import Optional,  List, Any
from slopguard.models import Finding, Severity, Confidence, Category
from slopguard.rules.base import BaseRule
from slopguard.parsers.base import BaseParser


class FakeEdgeCaseRule(BaseRule):
    def __init__(self, config_options: Optional[dict] = None):
        super().__init__("fake_edge_case_handling", config_options)

    def evaluate(
        self, file_path: str, code: str, parsed_ast: Any, parser: BaseParser
    ) -> List[Finding]:
        findings = []
        for i, line in enumerate(code.splitlines()):
            if (
                "if" in line
                and "is None:" in line
                and "return None" in code.splitlines()[i : i + 2][-1]
            ):
                findings.append(
                    Finding(
                        rule_id=self.rule_id,
                        title="Suspicious Edge Case Wrapping",
                        severity=Severity.LOW,
                        confidence=Confidence.LOW,
                        file_path=file_path,
                        line_number=i + 1,
                        short_explanation="Redundant None-check that suppresses errors.",
                        why_it_matters="If `x` cannot theoretically be None, checking it creates dead branches and hides type errors elsewhere.",
                        suggested_remediation="Rely on type checkers and remove defensive `None` propagation unless strictly supported.",
                        categories=[Category.TRUSTWORTHINESS],
                    )
                )
        return findings
