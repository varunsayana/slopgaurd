import ast
from typing import Optional,  List, Any
from slopguard.models import Finding, Severity, Confidence, Category, Scope
from slopguard.rules.base import BaseRule
from slopguard.parsers.base import BaseParser
from slopguard.parsers.python_parser import PythonParser


class UnnecessaryDataCopyRule(BaseRule):
    def __init__(self, config_options: Optional[dict] = None):
        super().__init__("unnecessary_data_copy", config_options)

    def evaluate(
        self, file_path: str, code: str, parsed_ast: Any, parser: BaseParser
    ) -> List[Finding]:
        findings = []
        if isinstance(parser, PythonParser) and parsed_ast:
            for node in ast.walk(parsed_ast):
                if (
                    isinstance(node, ast.Call)
                    and getattr(node.func, "id", "") == "list"
                ):
                    if (
                        len(node.args) == 1
                        and isinstance(node.args[0], ast.Call)
                        and getattr(node.args[0].func, "id", "") == "list"
                    ):
                        findings.append(
                            Finding(
                                rule_id=self.rule_id,
                                title="Unnecessary Data Copy",
                                severity=Severity.MEDIUM,
                                confidence=Confidence.HIGH,
                                scope=Scope.LINE,
                                file_path=file_path,
                                line_number=node.lineno,
                                short_explanation="Unnecessary nested list() wrapping creating redundant copies.",
                                why_it_matters="Copying large structures burns RAM and CPU cycles for no functional benefit.",
                                suggested_remediation="Remove the redundant list() wrap or slice copy.",
                                categories=[Category.PERFORMANCE_RISK],
                            )
                        )
        return findings
