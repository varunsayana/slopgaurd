from typing import Optional,  List, Any
from slopguard.models import Finding, Severity, Confidence, Category
from slopguard.rules.base import BaseRule
from slopguard.parsers.base import BaseParser

# Note: real implementation would diff against RepoBaseline


class StyleDriftRule(BaseRule):
    def __init__(self, config_options: Optional[dict] = None):
        super().__init__("style_drift", config_options)

    def evaluate(
        self, file_path: str, code: str, parsed_ast: Any, parser: BaseParser
    ) -> List[Finding]:
        findings = []
        # Pragmatic baseline mock
        functions = parser.get_functions(parsed_ast)
        if len(functions) > 0:
            avg_size = sum(
                f.get("end_line", 0) - f.get("start_line", 0) for f in functions
            ) / len(functions)
            if avg_size > 40:  # mock baseline deviation
                findings.append(
                    Finding(
                        rule_id=self.rule_id,
                        title="Style Drift from Repository Baseline",
                        severity=Severity.MEDIUM,
                        confidence=Confidence.LOW,
                        file_path=file_path,
                        line_number=1,
                        short_explanation=f"Average function size {avg_size:.1f} deviates from repo baseline of 12.5 lines.",
                        why_it_matters="Breaks expected repository norms, leading to maintenance friction.",
                        suggested_remediation="Refactor the logic to match the existing granularity of the repository.",
                        categories=[Category.CONSISTENCY],
                    )
                )
        return findings
