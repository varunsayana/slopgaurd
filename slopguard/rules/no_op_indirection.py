from typing import Optional,  List, Any
from slopguard.models import Finding, Severity, Confidence, Category
from slopguard.rules.base import BaseRule
from slopguard.parsers.base import BaseParser


class NoOpIndirectionRule(BaseRule):
    def __init__(self, config_options: Optional[dict] = None):
        super().__init__("no_op_indirection", config_options)

    def evaluate(
        self, file_path: str, code: str, parsed_ast: Any, parser: BaseParser
    ) -> List[Finding]:
        findings = []
        classes = parser.get_classes(parsed_ast)
        for cls in classes:
            size = cls.get("end_line", 0) - cls.get("start_line", 0)
            if size <= 3:
                findings.append(
                    Finding(
                        rule_id=self.rule_id,
                        title="No-Op Indirection Class",
                        severity=Severity.MEDIUM,
                        confidence=Confidence.MEDIUM,
                        file_path=file_path,
                        line_number=cls["start_line"],
                        short_explanation=f"Class {cls['name']} is almost empty.",
                        why_it_matters="Building empty facades or trivial classes instead of using dicts or direct objects adds fake 'Enterprise' slop.",
                        suggested_remediation="Remove the class entirely.",
                        categories=[Category.NECESSITY, Category.SPECIFICITY],
                    )
                )
        return findings
