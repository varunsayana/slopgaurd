from typing import Optional,  List, Any
from slopguard.models import Finding, Severity, Confidence, Category
from slopguard.rules.base import BaseRule
from slopguard.parsers.base import BaseParser


class DuplicateHelperRule(BaseRule):
    def __init__(self, config_options: Optional[dict] = None):
        super().__init__("duplicate_helper_pattern", config_options)

    def evaluate(
        self, file_path: str, code: str, parsed_ast: Any, parser: BaseParser
    ) -> List[Finding]:
        findings = []
        functions = parser.get_functions(parsed_ast)
        names = [f["name"] for f in functions]

        if len(names) != len(set(names)):
            # In some languages identical names overwrite, but let's check basic collision
            findings.append(
                Finding(
                    rule_id=self.rule_id,
                    title="Duplicate Helper Pattern",
                    severity=Severity.LOW,
                    confidence=Confidence.MEDIUM,
                    file_path=file_path,
                    line_number=1,
                    short_explanation="Multiple helpers share extremely similar or identical names.",
                    why_it_matters="Suggests copy-pasting code with renamed variables instead of real generalizations.",
                    suggested_remediation="Refactor the duplicated blocks into a single parameterized function.",
                    categories=[Category.COHERENCE],
                )
            )
        return findings
