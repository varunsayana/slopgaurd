import ast
from typing import Any, Dict, List
from slopguard.parsers.base import BaseParser


class PythonParser(BaseParser):
    def parse(self, code: str) -> Any:
        try:
            return ast.parse(code)
        except SyntaxError:
            return None

    def get_functions(self, tree: Any) -> List[Dict[str, Any]]:
        functions: List[Any] = []
        if tree is None:
            return functions

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append(
                    {
                        "name": node.name,
                        "start_line": node.lineno,
                        "end_line": node.end_lineno,
                        "is_async": isinstance(node, ast.AsyncFunctionDef),
                        "node": node,
                        "docstring": ast.get_docstring(node),
                    }
                )
        return functions

    def get_classes(self, tree: Any) -> List[Dict[str, Any]]:
        classes: List[Any] = []
        if tree is None:
            return classes

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(
                    {
                        "name": node.name,
                        "start_line": node.lineno,
                        "end_line": node.end_lineno,
                        "node": node,
                    }
                )
        return classes

    def get_imports(self, tree: Any) -> List[Dict[str, Any]]:
        imports: List[Any] = []
        if tree is None:
            return imports

        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(
                    {
                        "node": node,
                        "start_line": node.lineno,
                        "end_line": getattr(node, "end_lineno", node.lineno),
                        "names": [alias.name for alias in node.names],
                    }
                )
        return imports
