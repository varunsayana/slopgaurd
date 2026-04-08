import ast
from typing import Optional,  List, Any
from slopguard.models import Finding, Severity, Confidence, Category
from slopguard.rules.base import BaseRule
from slopguard.parsers.base import BaseParser
from slopguard.parsers.python_parser import PythonParser


class UselessWrapperRule(BaseRule):
    def __init__(self, config_options: Optional[dict] = None):
        super().__init__("useless_wrapper_function", config_options)

    def evaluate(
        self, file_path: str, code: str, parsed_ast: Any, parser: BaseParser
    ) -> List[Finding]:
        findings = []
        functions = parser.get_functions(parsed_ast)

        for func in functions:
            lines = func.get("end_line", 0) - func.get("start_line", 0)
            node = func.get("node")
            if lines <= 3 and node:
                # If python, we check if it literally just returns exactly what it calls
                if isinstance(parser, PythonParser) and isinstance(
                    node, ast.FunctionDef
                ):
                    if len(node.body) == 1 and isinstance(node.body[0], ast.Return):
                        if isinstance(node.body[0].value, ast.Call):
                            findings.append(
                                Finding(
                                    rule_id=self.rule_id,
                                    title="Useless Wrapper Function",
                                    severity=Severity.MEDIUM,
                                    confidence=Confidence.HIGH,
                                    file_path=file_path,
                                    line_number=func["start_line"],
                                    short_explanation=f"Function `{func['name']}` appears to just return the result of another function call without adding logic.",
                                    why_it_matters="Adds needless indirection layers that increase cognitive overhead.",
                                    suggested_remediation="Inline the wrapped call directly at the call sites.",
                                    categories=[
                                        Category.NECESSITY,
                                        Category.SPECIFICITY,
                                    ],
                                )
                            )
        return findings
