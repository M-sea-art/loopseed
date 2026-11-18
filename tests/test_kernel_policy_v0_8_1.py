from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


class RuntimeObservationKernelTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        return (REPO_ROOT / relative).read_text(encoding="utf-8")

    def test_runtime_plugin_and_usage_guide_versions_match(self) -> None:
        plugin = json.loads(self.read(".codex-plugin/plugin.json"))
        version = plugin["version"]

        types_text = self.read("skills/loopseed/scripts/one_shotted_types.py")
        match = re.search(r'^VERSION = "([^"]+)"$', types_text, re.MULTILINE)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), version)

        guide = self.read("docs/usage-guide.zh-CN.md")
        self.assertIn(f'loopseed_version: "{version}"', guide)

        critic = self.read("docs/oneshot-spec-compiler/critic-loop.yaml")
        self.assertIn(f'version: "{version}"', critic)

    def test_default_plugin_and_skill_buttons_invoke_an_ordinary_vision(self) -> None:
        interface = json.loads(self.read(".codex-plugin/plugin.json"))["interface"]
        agent = self.read("skills/loopseed/agents/openai.yaml")
        prompt = next(line.split(":", 1)[1].strip() for line in agent.splitlines()
                      if line.lstrip().startswith("default_prompt:"))
        for entry in (interface["defaultPrompt"][0], json.loads(prompt)):
            with self.subTest(entry=entry):
                command, first_word, *_ = entry.split(maxsplit=2)
                self.assertEqual(command, "$loopseed")
                self.assertNotEqual(first_word, "one-shotted")
        self.assertTrue(any(p.startswith("$loopseed one-shotted ") for p in interface["defaultPrompt"]))
        self.assertIn("allow_implicit_invocation: false", agent)

    def test_seed_kernel_requires_motion_evidence_when_motion_matters(self) -> None:
        methods = self.read("skills/loopseed/references/quality-methods.md")
        critic = self.read("docs/oneshot-spec-compiler/critic-loop.yaml")
        self.assertIn("Judge games in motion when motion matters", methods)
        self.assertIn("still_image_win_cannot_prove_motion_interaction_timing_camera_or_game_feel_superiority", critic)
        self.assertIn("motion_claims_have_motion_evidence_when_applicable", critic)

    def test_fresh_critic_is_first_hand_when_runtime_is_available(self) -> None:
        methods = self.read("skills/loopseed/references/quality-methods.md")
        critic = self.read("docs/oneshot-spec-compiler/critic-loop.yaml")
        self.assertIn("Critics inspect first-hand", methods)
        self.assertIn("critic_launches_plays_operates_or_views_the_real_candidate_when_capability_permits", critic)
        self.assertIn("critic_prefers_critic_owned_captures_over_builder_selected_interpretation", critic)

    def test_generated_assets_require_integrated_product_judgment(self) -> None:
        methods = self.read("skills/loopseed/references/quality-methods.md")
        critic = self.read("docs/oneshot-spec-compiler/critic-loop.yaml")
        self.assertIn("Judge generated assets in product context", methods)
        self.assertIn("generated_assets_are_judged_in_integrated_product_context_when_context_affects_quality", critic)
        self.assertIn("integrated_asset_claims_have_in_product_evidence_when_applicable", critic)

    def test_major_fanout_wave_requires_whole_product_reglobalization(self) -> None:
        methods = self.read("skills/loopseed/references/quality-methods.md")
        critic = self.read("docs/oneshot-spec-compiler/critic-loop.yaml")
        self.assertIn("Re-globalize after Fan-out", methods)
        self.assertIn("after_each_major_parallel_improvement_wave", critic)
        self.assertIn("use_one_fresh_whole_product_critic_across_the_integrated_result", critic)

    def test_synthetic_bar_is_fallback_not_behavioral_substitute(self) -> None:
        methods = self.read("skills/loopseed/references/quality-methods.md")
        critic = self.read("docs/oneshot-spec-compiler/critic-loop.yaml")
        self.assertIn("Synthetic Bar", methods)
        self.assertIn("synthetic_bar_must_be_frozen_before_judging_the_corresponding_candidate_generation", critic)
        self.assertIn("synthetic_visual_bar_cannot_substitute_for_behavior_interaction_or_performance_evidence", critic)


if __name__ == "__main__":
    unittest.main()
