import ast
from typing import Optional,  List, Any
from slopguard.models import Finding, Severity, Confidence, Category, Scope
from slopguard.rules.base import BaseRule
from slopguard.parsers.base import BaseParser
from slopguard.parsers.python_parser import PythonParser


class SyncBlockingRule(BaseRule):
    def __init__(self, config_options: Optional[dict] = None):
        super().__init__("sync_blocking_in_async_context", config_options)

    def evaluate(
        self, file_path: str, code: str, parsed_ast: Any, parser: BaseParser
    ) -> List[Finding]:
        findings = []
        if isinstance(parser, PythonParser) and parsed_ast:
            for node in ast.walk(parsed_ast):
                if isinstance(node, ast.AsyncFunctionDef):
                    for subnode in ast.walk(node):
                        if isinstance(subnode, ast.Call) and isinstance(
                            subnode.func, ast.Attribute
                        ):
                            # Looking for common blocking calls: requests.get, time.sleep
                            if subnode.func.attr in (
                                "sleep",
                                "get",
                                "post",
                                "put",
                                "delete",
                            ) and getattr(subnode.func.value, "id", "") in (
                                "time",
                                "requests",
                            ):
                                findings.append(
                                    Finding(
                                        rule_id=self.rule_id,
                                        title="Synchronous Blocking in Async Context",
                                        severity=Severity.HIGH,
                                        confidence=Confidence.HIGH,
                                        scope=Scope.LINE,
                                        file_path=file_path,
                                        line_number=subnode.lineno,
                                        short_explanation=f"Found synchronous blocking call '{getattr(subnode.func.value, 'id', '')}.{subnode.func.attr}' inside async function '{node.name}'.",
                                        why_it_matters="Blocking calls inside an async event loop starve the entire runtime, destroying concurrency.",
                                        suggested_remediation="Use async alternatives like 'asyncio.sleep' or 'httpx/aiohttp' instead.",
                                        categories=[Category.PERFORMANCE_RISK],
                                    )
                                )
        return findings
