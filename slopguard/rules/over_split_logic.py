from typing import Optional,  List, Any
from slopguard.models import Finding, Severity, Confidence, Category
from slopguard.rules.base import BaseRule
from slopguard.parsers.base import BaseParser


class OverSplitLogicRule(BaseRule):
    def __init__(self, config_options: Optional[dict] = None):
        super().__init__("over_split_logic", config_options)

    def evaluate(
        self, file_path: str, code: str, parsed_ast: Any, parser: BaseParser
    ) -> List[Finding]:
        findings = []
        if len(parser.get_functions(parsed_ast)) > 10 and len(code.splitlines()) < 80:
            findings.append(
                Finding(
                    rule_id=self.rule_id,
                    title="Overly Split Logic",
                    severity=Severity.LOW,
                    confidence=Confidence.LOW,
                    file_path=file_path,
                    line_number=1,
                    short_explanation="High density of small functions compared to total file length.",
                    why_it_matters="Jumping through 8 function calls for what could be 15 linear lines of code makes tracking state hard.",
                    suggested_remediation="Flatten the call stack.",
                    categories=[Category.SPECIFICITY],
                )
            )
        return findings
