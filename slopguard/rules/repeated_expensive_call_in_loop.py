import ast
from typing import Optional,  List, Any
from slopguard.models import Finding, Severity, Confidence, Category, Scope
from slopguard.rules.base import BaseRule
from slopguard.parsers.base import BaseParser
from slopguard.parsers.python_parser import PythonParser


class RepeatedExpensiveCallRule(BaseRule):
    def __init__(self, config_options: Optional[dict] = None):
        super().__init__("repeated_expensive_call_in_loop", config_options)

    def evaluate(
        self, file_path: str, code: str, parsed_ast: Any, parser: BaseParser
    ) -> List[Finding]:
        findings = []
        if isinstance(parser, PythonParser) and parsed_ast:
            for loop_node in ast.walk(parsed_ast):
                if isinstance(loop_node, (ast.For, ast.While)):
                    for node in ast.walk(loop_node):
                        if isinstance(node, ast.Call):
                            name = ""
                            if isinstance(node.func, ast.Name):
                                name = node.func.id
                            elif isinstance(node.func, ast.Attribute):
                                name = node.func.attr

                            if name in ("get", "post", "query", "execute", "read_text"):
                                findings.append(
                                    Finding(
                                        rule_id=self.rule_id,
                                        title="Repeated Expensive Call In Loop",
                                        severity=Severity.HIGH,
                                        confidence=Confidence.MEDIUM,
                                        scope=Scope.LINE,
                                        file_path=file_path,
                                        line_number=node.lineno,
                                        short_explanation=f"Expensive call '{name}' found inside a loop.",
                                        why_it_matters="Network/DB queries inside loops create massive N+1 performance bottlenecks.",
                                        suggested_remediation="Hoister the call outside the loop or batch aggregate the query.",
                                        categories=[Category.PERFORMANCE_RISK],
                                    )
                                )
        return findings
