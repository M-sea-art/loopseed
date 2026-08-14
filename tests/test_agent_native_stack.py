import argparse
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "loopseed" / "scripts" / "agent_native_stack.py"
SPEC = importlib.util.spec_from_file_location("agent_native_stack", SCRIPT)
stack = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(stack)


class AgentNativeStackTests(unittest.TestCase):
    def test_init_creates_engine_neutral_state(self):
        with tempfile.TemporaryDirectory() as temp:
            paths = stack.init_state(temp, "wuxia-sect")
            world = json.loads(Path(paths["world_plan"]).read_text(encoding="utf-8"))
            registry = json.loads(Path(paths["registry"]).read_text(encoding="utf-8"))
            self.assertEqual(world["world_id"], "wuxia-sect")
            self.assertEqual(world["units"], "meters")
            self.assertEqual(world["camera_contracts"], [])
            self.assertEqual(registry, {"stack_version": "1.0", "capabilities": []})
            self.assertTrue(Path(paths["harvest"]).exists())

    def test_register_capability_and_reject_duplicate(self):
        with tempfile.TemporaryDirectory() as temp:
            args = argparse.Namespace(
                root=temp,
                world_id="game",
                id="godot.runtime.capture",
                domain="engine",
                provider="godot-ai",
                description="Capture observable runtime evidence",
                engine=["godot", "godot"],
                input=["running-scene"],
                output=["screenshot"],
                tool=["godot-ai"],
                evidence=["runtime-artifact"],
                ownership="isolated",
                cost="low",
                status="experimental",
                fallback="manual-capture",
                source_repo="hi-godot/godot-ai",
                source_reference="",
                source_evidence=[],
            )
            record = stack.register_capability(args)
            self.assertEqual(record["engine_support"], ["godot"])
            with self.assertRaisesRegex(ValueError, "already registered"):
                stack.register_capability(args)

    def test_harvest_records_template_gap_without_auto_promotion(self):
        with tempfile.TemporaryDirectory() as temp:
            args = argparse.Namespace(
                root=temp,
                world_id="wuxia",
                actor="visual-critic",
                source="gate ROOF-02",
                kind="template_gap",
                summary="Current roof factory cannot express the target eave silhouette",
                evidence=["captures/roof-02.png"],
                capability_id="wuxia.eave.curved-v2",
                next_action="Implement and verify a reusable eave factory",
            )
            event = stack.harvest(args)
            self.assertFalse(event["promoted"])
            self.assertEqual(event["proposed_capability_id"], "wuxia.eave.curved-v2")
            harvest_path = Path(temp) / ".loopseed" / "agent-native-stack-v1" / "harvest.jsonl"
            lines = harvest_path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 1)
            self.assertEqual(json.loads(lines[0])["kind"], "template_gap")


if __name__ == "__main__":
    unittest.main()
