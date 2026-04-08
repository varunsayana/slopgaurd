from typing import Optional,  List, Any
from slopguard.models import Finding, Severity, Confidence, Category
from slopguard.rules.base import BaseRule
from slopguard.parsers.base import BaseParser


class AbstractionInflationRule(BaseRule):
    def __init__(self, config_options: Optional[dict] = None):
        super().__init__("abstraction_inflation", config_options)

    def evaluate(
        self, file_path: str, code: str, parsed_ast: Any, parser: BaseParser
    ) -> List[Finding]:
        findings = []
        functions = parser.get_functions(parsed_ast)

        if len(functions) > 10:
            avg_size = sum(
                f.get("end_line", 0) - f.get("start_line", 0) for f in functions
            ) / len(functions)
            if avg_size < 5:
                findings.append(
                    Finding(
                        rule_id=self.rule_id,
                        title="Abstraction Inflation",
                        severity=Severity.MEDIUM,
                        confidence=Confidence.MEDIUM,
                        file_path=file_path,
                        line_number=1,
                        short_explanation=f"Found {len(functions)} very small functions (avg {avg_size:.1f} lines) in one file.",
                        why_it_matters="Excessive splintering of simple logic makes the codebase harder to read top-to-bottom.",
                        suggested_remediation="Consolidate trivial helpers into inline logic.",
                        categories=[Category.NECESSITY, Category.SPECIFICITY],
                    )
                )
        return findings
