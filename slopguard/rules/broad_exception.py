import ast
from typing import Optional,  List, Any
from slopguard.models import Finding, Severity, Confidence, Category
from slopguard.rules.base import BaseRule
from slopguard.parsers.base import BaseParser
from slopguard.parsers.python_parser import PythonParser


class BroadExceptionRule(BaseRule):
    def __init__(self, config_options: Optional[dict] = None):
        super().__init__("broad_exception", config_options)

    def evaluate(
        self, file_path: str, code: str, parsed_ast: Any, parser: BaseParser
    ) -> List[Finding]:
        findings = []
        if isinstance(parser, PythonParser) and parsed_ast:
            for node in ast.walk(parsed_ast):
                if isinstance(node, ast.ExceptHandler):
                    # check if catching bare Exception or no type specified
                    is_broad = False
                    if node.type is None:
                        is_broad = True  # except:
                    elif isinstance(node.type, ast.Name) and node.type.id in (
                        "Exception",
                        "BaseException",
                    ):
                        is_broad = True  # except Exception:

                    if is_broad:
                        findings.append(
                            Finding(
                                rule_id=self.rule_id,
                                title="Broad Exception Swallowed",
                                severity=Severity.HIGH,
                                confidence=Confidence.HIGH,
                                file_path=file_path,
                                line_number=node.lineno,
                                short_explanation="Code catches a generic Exception without narrowing.",
                                why_it_matters="Hides unexpected critical errors in production, making debugging extremely difficult.",
                                suggested_remediation="Catch specific exceptions like ValueError or KeyError.",
                                categories=[
                                    Category.TRUSTWORTHINESS,
                                    Category.SPECIFICITY,
                                ],
                            )
                        )
        return findings
