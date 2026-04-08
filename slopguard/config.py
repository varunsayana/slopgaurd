"""
Configuration schemas for SlopGuard.
"""

from pydantic import BaseModel, Field
from typing import Dict, List
import yaml  # type: ignore
import os

from slopguard.models import RuleConfig

DEFAULT_CONFIG_PATH = ".slopguard.yml"


class ThresholdsConfig(BaseModel):
    fail_score: int = Field(
        default=80, description="Score threshold to return non-zero exit code."
    )
    warn_score: int = Field(
        default=50, description="Score threshold to emit warnings explicitly."
    )


class PathsConfig(BaseModel):
    include: List[str] = Field(default=["**/*.py", "**/*.js", "**/*.ts"])
    exclude: List[str] = Field(
        default=[
            "tests/**",
            "docs/**",
            "node_modules/**",
            "venv/**",
            ".venv/**",
            "dist/**",
        ]
    )


class BaselineConfig(BaseModel):
    enabled: bool = True
    sample_size: int = 200


class AutofixConfig(BaseModel):
    enabled: bool = False
    safe_only: bool = True


class CiConfig(BaseModel):
    fail_on_score: int = 80
    fail_on_error: bool = True


class ReviewdogConfig(BaseModel):
    enabled: bool = True
    reporter: str = "github-pr-review"
    level: str = "warning"


class PerformanceConfig(BaseModel):
    hot_paths: List[str] = Field(default_factory=lambda: ["src/api/**", "src/core/**"])


class SlopGuardConfig(BaseModel):
    version: int = 1
    thresholds: ThresholdsConfig = Field(default_factory=ThresholdsConfig)
    paths: PathsConfig = Field(default_factory=PathsConfig)
    baseline: BaselineConfig = Field(default_factory=BaselineConfig)
    rules: Dict[str, RuleConfig] = Field(default_factory=dict)
    autofix: AutofixConfig = Field(default_factory=AutofixConfig)

    ci: CiConfig = Field(default_factory=CiConfig)
    reviewdog: ReviewdogConfig = Field(default_factory=ReviewdogConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)

    @classmethod
    def load(cls, path: str = DEFAULT_CONFIG_PATH) -> "SlopGuardConfig":
        """Loads configuration from YAML file, fallback to defaults."""
        if not os.path.exists(path):
            return cls()
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if data is None:
                return cls()
            return cls(**data)

    def save(self, path: str = DEFAULT_CONFIG_PATH) -> None:
        """Saves current configuration to a YAML file."""
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(self.model_dump(), f, sort_keys=False)
