import os
from typing import Dict, Any
from slopguard.config import SlopGuardConfig
from slopguard.models import RunContext, Scope
from slopguard.engine.diff_loader import DiffLoader
from slopguard.engine.scoring import ScoringEngine

from slopguard.parsers.python_parser import PythonParser
from slopguard.parsers.javascript_parser import JavascriptParser, TypescriptParser
from slopguard.parsers.generic import GenericParser

# Import rules registry
from slopguard.rules import registry


class Analyzer:
    def __init__(self, config: SlopGuardConfig, context: RunContext):
        self.config = config
        self.context = context
        self.diff_loader = DiffLoader(context.repo_path)
        self.scoring = ScoringEngine()
        self.parsers = {
            ".py": PythonParser(),
            ".js": JavascriptParser(),
            ".jsx": JavascriptParser(),
            ".ts": TypescriptParser(),
            ".tsx": TypescriptParser(),
        }
        self.generic_parser = GenericParser()

    def run(self) -> Dict[str, Any]:
        """Runs the complete analysis pipeline."""
        patch_set = None
        if self.context.base_ref and self.context.head_ref:
            patch_set = self.diff_loader.get_diff_from_refs(
                self.context.base_ref, self.context.head_ref
            )
        elif self.context.is_staged_only:
            patch_set = self.diff_loader.get_diff_staged()
        elif self.context.patch_file:
            patch_set = self.diff_loader.load_patch_file(self.context.patch_file)
        elif self.context.single_file:
            patch_set = self.diff_loader.construct_file_diff(self.context.single_file)

        all_findings = []
        if not patch_set:
            return {
                "score": 100,
                "status": "Pass",
                "categories": {},
                "counts": {},
                "findings": [],
            }

        # Analyze each changed file
        for patched_file in patch_set:
            if not patched_file.is_added_file and not patched_file.is_modified_file:
                continue

            file_path = patched_file.path

            # Simple exclude
            if any(
                file_path.endswith(ext) for ext in [".json", ".md", ".txt", ".lock"]
            ):
                continue

            full_path = os.path.join(self.context.repo_path, file_path)
            if not os.path.exists(full_path):
                continue

            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                code = f.read()

            # Build changed lines map
            changed_lines = set()
            if patch_set:
                for hunk in patched_file:
                    for line in hunk:
                        if line.is_added:
                            changed_lines.add(line.target_line_no)

            ext = os.path.splitext(file_path)[1]
            parser = self.parsers.get(ext, self.generic_parser)
            parsed_ast = parser.parse(code)

            # Run enabled rules
            for rule_id, rule_class in registry.items():
                rule_config = self.config.rules.get(rule_id)
                if getattr(
                    rule_config, "enabled", True
                ):  # active by default if not set
                    opts = getattr(rule_config, "options", {}) if rule_config else {}
                    rule_instance = rule_class(opts)  # type: ignore
                    findings = rule_instance.evaluate(
                        file_path, code, parsed_ast, parser
                    )

                    # Optional severity override from config
                    if rule_config:
                        severity_opt = getattr(rule_config, "severity", None)
                        if severity_opt is not None:
                            for fnd in findings:
                                fnd.severity = severity_opt

                    # Apply diff filtering policy
                    for fnd in findings:
                        if not patch_set:
                            all_findings.append(fnd)
                            continue

                        is_changed = fnd.line_number in changed_lines

                        if fnd.scope == Scope.LINE:
                            if is_changed:
                                all_findings.append(fnd)
                        elif fnd.scope == Scope.FILE:
                            if fnd.caused_by_pr:
                                if not is_changed and changed_lines:
                                    fnd.line_number = min(
                                        changed_lines,
                                        key=lambda x: abs(x - (fnd.line_number or 1)),
                                    )
                                elif not changed_lines:
                                    fnd.line_number = 1
                                all_findings.append(fnd)

        results = self.scoring.score(all_findings)
        results["findings"] = all_findings
        return results
