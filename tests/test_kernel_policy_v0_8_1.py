from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


class RuntimeObservationKernelTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        return (REPO_ROOT / relative).read_text(encoding="utf-8")

    def test_runtime_plugin_and_usage_guide_versions_match_0_8_1(self) -> None:
        plugin = json.loads(self.read(".codex-plugin/plugin.json"))
        self.assertEqual(plugin["version"], "0.8.1")

        types_text = self.read("skills/loopseed/scripts/one_shotted_types.py")
        match = re.search(r'^VERSION = "([^"]+)"$', types_text, re.MULTILINE)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), "0.8.1")

        guide = self.read("docs/usage-guide.zh-CN.md")
        self.assertIn('loopseed_version: "0.8.1"', guide)

        critic = self.read("docs/oneshot-spec-compiler/critic-loop.yaml")
        self.assertIn('version: "0.8.1"', critic)

    def test_seed_kernel_requires_motion_evidence_when_motion_matters(self) -> None:
        skill = self.read("skills/loopseed/SKILL.md")
        critic = self.read("docs/oneshot-spec-compiler/critic-loop.yaml")
        self.assertIn("Judge games in motion when motion matters", skill)
        self.assertIn("still_image_win_cannot_prove_motion_interaction_timing_camera_or_game_feel_superiority", critic)
        self.assertIn("motion_claims_have_motion_evidence_when_applicable", critic)

    def test_fresh_critic_is_first_hand_when_runtime_is_available(self) -> None:
        skill = self.read("skills/loopseed/SKILL.md")
        critic = self.read("docs/oneshot-spec-compiler/critic-loop.yaml")
        self.assertIn("Critics inspect first-hand", skill)
        self.assertIn("critic_launches_plays_operates_or_views_the_real_candidate_when_capability_permits", critic)
        self.assertIn("critic_prefers_critic_owned_captures_over_builder_selected_interpretation", critic)

    def test_generated_assets_require_integrated_product_judgment(self) -> None:
        skill = self.read("skills/loopseed/SKILL.md")
        critic = self.read("docs/oneshot-spec-compiler/critic-loop.yaml")
        self.assertIn("Judge generated assets in product context", skill)
        self.assertIn("generated_assets_are_judged_in_integrated_product_context_when_context_affects_quality", critic)
        self.assertIn("integrated_asset_claims_have_in_product_evidence_when_applicable", critic)

    def test_major_fanout_wave_requires_whole_product_reglobalization(self) -> None:
        skill = self.read("skills/loopseed/SKILL.md")
        critic = self.read("docs/oneshot-spec-compiler/critic-loop.yaml")
        self.assertIn("Re-globalize after Fan-out", skill)
        self.assertIn("after_each_major_parallel_improvement_wave", critic)
        self.assertIn("use_one_fresh_whole_product_critic_across_the_integrated_result", critic)

    def test_synthetic_bar_is_fallback_not_behavioral_substitute(self) -> None:
        skill = self.read("skills/loopseed/SKILL.md")
        critic = self.read("docs/oneshot-spec-compiler/critic-loop.yaml")
        self.assertIn("Synthetic Bar", skill)
        self.assertIn("synthetic_bar_must_be_frozen_before_judging_the_corresponding_candidate_generation", critic)
        self.assertIn("synthetic_visual_bar_cannot_substitute_for_behavior_interaction_or_performance_evidence", critic)


if __name__ == "__main__":
    unittest.main()
