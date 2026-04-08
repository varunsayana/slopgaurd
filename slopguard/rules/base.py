from abc import ABC, abstractmethod
from typing import Optional,  List, Any
from slopguard.models import Finding
from slopguard.parsers.base import BaseParser


class BaseRule(ABC):
    def __init__(self, rule_id: str, config_options: Optional[dict] = None):
        self.rule_id = rule_id
        self.config_options = config_options or {}

    @abstractmethod
    def evaluate(
        self, file_path: str, code: str, parsed_ast: Any, parser: BaseParser
    ) -> List[Finding]:
        """
        Evaluates a single file and returns any matched slop patterns.
        """
        pass
