import json
from typing import Dict, Any


class SarifFormatter:
    def format(self, results: Dict[str, Any]) -> str:
        findings = results.get("findings", [])
        sarif: Dict[str, Any] = {
            "version": "2.1.0",
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "SlopGuard",
                            "informationUri": "https://github.com/slopguard/slopguard",
                            "rules": [],
                        }
                    },
                    "results": [],
                }
            ],
        }

        for f in findings:
            sarif["runs"][0]["results"].append(
                {
                    "ruleId": f.rule_id,
                    "message": {"text": f.short_explanation},
                    "locations": [
                        {
                            "physicalLocation": {
                                "artifactLocation": {"uri": f.file_path},
                                "region": {"startLine": f.line_number or 1},
                            }
                        }
                    ],
                }
            )

        return json.dumps(sarif, indent=2)
