import copy
import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validator", ROOT / "scripts" / "validate_creator_template.py")
validator = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(validator)


def sample_workflow():
    return {
        "name": "Create demo workflow with HTTP API",
        "active": False,
        "nodes": [
            {
                "id": "s1",
                "name": "Sticky Note",
                "type": "n8n-nodes-base.stickyNote",
                "typeVersion": 1,
                "position": [-500, -200],
                "parameters": {
                    "content": "# Demo\n### How it works\nRuns a demo.\n### Setup steps\nConfigure it.\n### Customization\nAdapt fields.",
                    "width": 300,
                    "height": 220,
                },
            },
            {
                "id": "s2",
                "name": "Sticky Note1",
                "type": "n8n-nodes-base.stickyNote",
                "typeVersion": 1,
                "position": [0, -200],
                "parameters": {
                    "content": "## Fetch data\nCalls the configured API.",
                    "width": 300,
                    "height": 180,
                    "color": 7,
                },
            },
            {
                "id": "n1",
                "name": "Start Demo",
                "type": "n8n-nodes-base.manualTrigger",
                "typeVersion": 1,
                "position": [50, 0],
                "parameters": {},
            },
            {
                "id": "n2",
                "name": "Fetch Demo Data",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [350, 0],
                "parameters": {"url": "https://example.com/api"},
            },
        ],
        "connections": {
            "Start Demo": {
                "main": [[{"node": "Fetch Demo Data", "type": "main", "index": 0}]]
            }
        },
        "settings": {"executionOrder": "v1"},
        "meta": {"templateCredsSetupCompleted": False},
    }


class ValidatorRegressionTests(unittest.TestCase):
    def test_valid_shape_has_no_issues(self):
        self.assertEqual(validator.validate_workflow_shape(sample_workflow()), [])

    def test_missing_node_id_is_detected(self):
        wf = sample_workflow()
        del wf["nodes"][2]["id"]
        self.assertIn("node_2_missing_or_invalid_id", validator.validate_workflow_shape(wf))

    def test_workflow_settings_change_is_detected(self):
        baseline = sample_workflow()
        candidate = copy.deepcopy(baseline)
        candidate["settings"]["executionOrder"] = "v0"
        report = validator.baseline_report(candidate, baseline)
        self.assertFalse(report["workflow_settings_match"])

    def test_error_workflow_removal_is_allowed_for_public_candidate(self):
        baseline = sample_workflow()
        baseline["settings"]["errorWorkflow"] = "instance-workflow-id"
        candidate = copy.deepcopy(baseline)
        del candidate["settings"]["errorWorkflow"]
        report = validator.baseline_report(candidate, baseline)
        self.assertTrue(report["workflow_settings_match"])

    def test_hardcoded_email_is_detected_outside_functional_parameters(self):
        wf = sample_workflow()
        wf["nodes"][0]["parameters"]["content"] += "\nContact owner@private-domain.test"
        self.assertIn("owner@private-domain.test", validator.private_leak_checks(wf)["hardcoded_emails"])


if __name__ == "__main__":
    unittest.main()
