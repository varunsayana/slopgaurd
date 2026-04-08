from typing import Optional,  List, Any
from slopguard.models import Finding, Severity, Confidence, Category
from slopguard.rules.base import BaseRule
from slopguard.parsers.base import BaseParser
import re


class SuspiciousCommentDensityRule(BaseRule):
    def __init__(self, config_options: Optional[dict] = None):
        super().__init__("suspicious_comment_density", config_options)
        self.max_ratio = self.config_options.get("max_comment_ratio", 0.35)

    def evaluate(
        self, file_path: str, code: str, parsed_ast: Any, parser: BaseParser
    ) -> List[Finding]:
        findings = []
        lines = code.splitlines()
        if not lines:
            return []

        comment_lines = sum(1 for line in lines if re.match(r"^\s*(#|//|\*|/\*)", line))
        ratio = comment_lines / len(lines)

        if ratio > self.max_ratio and len(lines) > 20:  # arbitrary minimum threshold
            findings.append(
                Finding(
                    rule_id=self.rule_id,
                    title="Suspiciously High Comment Density",
                    severity=Severity.MEDIUM,
                    confidence=Confidence.MEDIUM,
                    file_path=file_path,
                    line_number=1,
                    short_explanation=f"Comment ratio is {ratio:.2f}, which exceeds threshold {self.max_ratio:.2f}.",
                    why_it_matters="Over-commenting often restates obvious code behavior rather than answering 'why', hurting readability.",
                    suggested_remediation="Remove comments that merely translate the syntax into English.",
                    categories=[Category.CONSISTENCY],
                )
            )
        return findings
