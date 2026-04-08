from typing import Optional
from slopguard.rules.broad_exception import BroadExceptionRule
from slopguard.rules.dead_code_signals import DeadCodeSignalsRule
from slopguard.rules.suspicious_comment_density import SuspiciousCommentDensityRule
from slopguard.rules.useless_wrapper import UselessWrapperRule
from slopguard.rules.abstraction_inflation import AbstractionInflationRule
from slopguard.rules.duplicate_helper import DuplicateHelperRule
from slopguard.rules.unnecessary_config_surface import UnnecessaryConfigRule
from slopguard.rules.repeated_expensive_call_in_loop import RepeatedExpensiveCallRule
from slopguard.rules.unnecessary_data_copy import UnnecessaryDataCopyRule
from slopguard.rules.sync_blocking_in_async_context import SyncBlockingRule
from slopguard.rules.style_drift import StyleDriftRule
from slopguard.rules.over_split_logic import OverSplitLogicRule
from slopguard.rules.fake_edge_case_handling import FakeEdgeCaseRule
from slopguard.rules.no_op_indirection import NoOpIndirectionRule

registry = {
    "broad_exception": BroadExceptionRule,
    "dead_code_signals": DeadCodeSignalsRule,
    "suspicious_comment_density": SuspiciousCommentDensityRule,
    "useless_wrapper_function": UselessWrapperRule,
    "abstraction_inflation": AbstractionInflationRule,
    "duplicate_helper_pattern": DuplicateHelperRule,
    "unnecessary_config_surface": UnnecessaryConfigRule,
    "repeated_expensive_call_in_loop": RepeatedExpensiveCallRule,
    "unnecessary_data_copy": UnnecessaryDataCopyRule,
    "sync_blocking_in_async_context": SyncBlockingRule,
    "style_drift": StyleDriftRule,
    "over_split_logic": OverSplitLogicRule,
    "fake_edge_case_handling": FakeEdgeCaseRule,
    "no_op_indirection": NoOpIndirectionRule,
}
