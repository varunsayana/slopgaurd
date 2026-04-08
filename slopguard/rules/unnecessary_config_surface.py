from typing import Optional,  List, Any
from slopguard.models import Finding, Severity, Confidence, Category
from slopguard.rules.base import BaseRule
from slopguard.parsers.base import BaseParser


class UnnecessaryConfigRule(BaseRule):
    def __init__(self, config_options: Optional[dict] = None):
        super().__init__("unnecessary_config_surface", config_options)

    def evaluate(
        self, file_path: str, code: str, parsed_ast: Any, parser: BaseParser
    ) -> List[Finding]:
        findings = []
        # Pragmatic check: looking for many default boolean flags in signatures visually

        for i, line in enumerate(code.splitlines()):
            if "def " in line and line.count("=False") + line.count("=True") > 3:
                findings.append(
                    Finding(
                        rule_id=self.rule_id,
                        title="Unnecessary Configuration Surface",
                        severity=Severity.LOW,
                        confidence=Confidence.LOW,
                        file_path=file_path,
                        line_number=i + 1,
                        short_explanation="Function defines many default boolean parameters.",
                        why_it_matters="Explodes the configuration surface area for local use cases, signaling overengineering.",
                        suggested_remediation="Remove flags and handle narrow logic directly or pass an options object.",
                        categories=[Category.SPECIFICITY],
                    )
                )
        return findings
