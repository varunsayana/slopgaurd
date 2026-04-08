from typing import Optional,  List, Any
from slopguard.models import Finding, Severity, Confidence, Category
from slopguard.rules.base import BaseRule
from slopguard.parsers.base import BaseParser


class DeadCodeSignalsRule(BaseRule):
    def __init__(self, config_options: Optional[dict] = None):
        super().__init__("dead_code_signals", config_options)

    def evaluate(
        self, file_path: str, code: str, parsed_ast: Any, parser: BaseParser
    ) -> List[Finding]:
        findings = []
        # Pragmatic baseline detection
        lines = code.splitlines()
        for i, line in enumerate(lines):
            line_str = line.strip()
            if line_str == "pass" or line_str == "return None":
                # Check for empty blocks which often define useless branches
                findings.append(
                    Finding(
                        rule_id=self.rule_id,
                        title="Suspicious Dead Code Signal",
                        severity=Severity.LOW,
                        confidence=Confidence.MEDIUM,
                        file_path=file_path,
                        line_number=i + 1,
                        short_explanation="Found trivial placeholder 'pass' or redundant 'return None' logic.",
                        why_it_matters="Dead branches and placeholders indicate unfinished AI or sloppy human code.",
                        suggested_remediation="Remove empty functions or branches if they do nothing.",
                        categories=[Category.NECESSITY, Category.COHERENCE],
                    )
                )
        return findings
