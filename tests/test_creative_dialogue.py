from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "skills" / "loopseed" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from one_shotted_core import (  # noqa: E402
    OneShottedError,
    add_gate,
    finalize,
    initialize,
    lock_creative_brief,
    record_dialogue_turn,
    status,
    transition,
    validate,
)


class CreativeDialogueTests(unittest.TestCase):
    def make_root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        (root / ".git").mkdir()
        return temporary, root

    def dialogue(self, root: Path) -> list[str]:
        first = record_dialogue_turn(
            root,
            "model",
            "question",
            "The strongest idea is an autonomous sect whose disciples' desires pressure the player. Choose the production ambition.",
            effects=["preserve", "amplify"],
            advances=["production_mode", "player_promise"],
            options=[
                "A|Focused|Prove one complete management loop quickly",
                "B|Studio|Build a presentation-ready vertical slice with art and game-feel contracts",
                "C|Moonshot|Amplify the living-sect fantasy with aggressive but bounded production",
            ],
            recommended="B",
        )
        answer = record_dialogue_turn(
            root,
            "user",
            "answer",
            "Use Studio as the base, but preserve the Moonshot idea that disciples' memories and desires drive events.",
        )
        second = record_dialogue_turn(
            root,
            "model",
            "question",
            "Keep indirect control as the core. Choose how the first slice proves that the sect is alive.",
            effects=["continue", "complete", "offer_options"],
            advances=["core_loop", "hero_moment"],
            options=[
                "A|Three-day sect crisis|A compact loop where autonomous disciples create visible consequences",
                "B|Single cinematic scene|Maximum spectacle but weak management proof",
                "C|Large sandbox|More breadth but lower completion confidence",
            ],
            recommended="A",
        )
        decision = record_dialogue_turn(
            root,
            "user",
            "decision",
            "Choose A. Preserve indirect control, inherited memories, and a high-fidelity sect cutaway as the hero view.",
        )
        return [first["event_id"], answer["event_id"], second["event_id"], decision["event_id"]]

    def brief(self, event_ids: list[str], *, mode: str = "studio") -> dict[str, object]:
        return {
            "project_domain": "game",
            "production_mode": mode,
            "seed_intent": "Create a wuxia sect management game driven by disciple desire and memory.",
            "product_outcome": "A presentation-ready three-day sect-management vertical slice.",
            "north_star": "The player feels the sect is alive because disciples act from their own motives.",
            "original_user_ideas": ["autonomous disciples", "inherited memories", "indirect control"],
            "preserved_ideas": ["desire-driven characters", "wuxia sect", "memory across lives"],
            "revisions": ["Direct unit control becomes indirect rules, resources, and attention."],
            "amplifications": ["One crisis makes conflicting memories visibly change relationships and choices."],
            "decisions": ["Studio base", "three-day crisis", "high-fidelity cutaway hero view"],
            "bounded_scope": ["one sect", "three in-game days", "one crisis", "one complete management loop"],
            "non_goals": ["open-world jianghu", "full combat campaign"],
            "must_not_lose": ["indirect control", "desire-driven disciples", "finished art rather than blockout"],
            "reference_roles": ["Fallout Shelter: readable cutaway only", "Cultist Simulator: object-like narrative only"],
            "required_evidence": ["complete playthrough", "fixed hero screenshot", "performance budget report"],
            "game": {
                "player_promise": "Shape a living sect without directly puppeteering its people.",
                "player_role": "Sect leader who influences rules, resources, relationships, and attention.",
                "core_loop": "Observe motives, allocate scarce resources, make a sect decision, witness autonomous consequences.",
                "world_response": "Disciples remember, resent, cooperate, leave, or reinterpret orders based on desire and memory.",
                "unique_hook": "Characters' desires and inherited memories drive the player rather than the reverse.",
                "art_direction": "High-density handmade wuxia miniature cutaway with restrained cinematic light.",
                "game_feel": "Immediate readable state changes, grounded sound, deliberate camera emphasis, no dashboard feel.",
                "hero_moment": "The full sect cutaway visibly erupts into one connected crisis caused by three disciples' motives.",
                "vertical_slice": "A complete three-day crisis from arrival through consequence and restart.",
                "asset_strategy": "Reuse project-native assets where final-quality; generate and replace all remaining placeholders before visual PASS.",
                "performance_budget": {"fps": 60, "draw_calls": 300, "triangles": 2200000},
            },
            "general": {
                "user_job": "",
                "primary_flow": "",
                "artifact_type": "",
                "target_stage": "",
                "success_metrics": "",
            },
            "moonshot": {
                "ambition_expansion": "Make the autonomous sect feel startlingly alive in one bounded crisis." if mode == "moonshot" else "",
                "scope_guard": "Deepen one crisis and one hero view; do not add an open world." if mode == "moonshot" else "",
            },
            "authorization": {"user_event_id": event_ids[-1]},
            "dialogue_event_ids": event_ids,
        }

    def test_game_goal_enters_creative_dialogue(self) -> None:
        temporary, root = self.make_root()
        with temporary:
            result = initialize(root, "制作一个弟子由欲望与记忆驱动的武侠门派经营游戏")
            self.assertEqual(result["project_domain"], "game")
            self.assertEqual(result["phase"], "CALIBRATE")
            self.assertEqual(result["production_mode"], "undecided")
            self.assertTrue((root / ".loopseed" / "one-shotted" / "creative-brief.json").is_file())

    def test_general_goal_keeps_direct_bind_by_default(self) -> None:
        temporary, root = self.make_root()
        with temporary:
            result = initialize(root, "Prepare a verified migration report")
            self.assertEqual(result["project_domain"], "general")
            self.assertEqual(result["phase"], "BIND")
            self.assertEqual(result["production_mode"], "focused")

    def test_clear_game_can_explicitly_use_direct_studio_path(self) -> None:
        temporary, root = self.make_root()
        with temporary:
            result = initialize(
                root,
                "Build a fully specified browser game vertical slice",
                dialogue="off",
            )
            self.assertEqual(result["project_domain"], "game")
            self.assertEqual(result["phase"], "BIND")
            self.assertEqual(result["production_mode"], "studio")
            self.assertEqual(result["calibration_status"], "SKIPPED")

    def test_model_question_requires_meaningful_options(self) -> None:
        temporary, root = self.make_root()
        with temporary:
            initialize(root, "Build a browser game")
            with self.assertRaisesRegex(OneShottedError, "between 2 and 4"):
                record_dialogue_turn(
                    root,
                    "model",
                    "question",
                    "Choose a production route.",
                    effects=["clarify"],
                    advances=["production_mode"],
                    options=["A|Focused|Fast"],
                    recommended="A",
                )

    def test_repeated_question_is_rejected(self) -> None:
        temporary, root = self.make_root()
        with temporary:
            initialize(root, "Build a browser game")
            question = {
                "actor": "model",
                "kind": "question",
                "summary": "Choose the production route.",
                "effects": ["clarify"],
                "advances": ["production_mode"],
                "options": [
                    "A|Focused|Fast complete result",
                    "B|Studio|Presentation-ready slice",
                ],
                "recommended": "B",
            }
            record_dialogue_turn(root, **question)
            record_dialogue_turn(root, "user", "answer", "Choose Studio.")
            with self.assertRaisesRegex(OneShottedError, "Do not repeat"):
                record_dialogue_turn(root, **question)

    def test_dialogue_round_limit_is_enforced(self) -> None:
        temporary, root = self.make_root()
        with temporary:
            initialize(root, "Build a browser game", max_dialogue_rounds=1)
            record_dialogue_turn(
                root,
                "model",
                "question",
                "Choose the production route.",
                effects=["clarify"],
                advances=["production_mode"],
                options=["A|Focused|Fast", "B|Studio|Polished"],
                recommended="B",
            )
            record_dialogue_turn(root, "user", "answer", "Choose Studio.")
            with self.assertRaisesRegex(OneShottedError, "round limit reached"):
                record_dialogue_turn(
                    root,
                    "model",
                    "question",
                    "Choose the hero moment.",
                    effects=["complete"],
                    advances=["hero_moment"],
                    options=["A|Crisis|Systemic", "B|Reveal|Cinematic"],
                    recommended="A",
                )

    def test_multiple_rounds_lock_one_shot_brief(self) -> None:
        temporary, root = self.make_root()
        with temporary:
            initialize(root, "制作一个武侠门派经营游戏")
            event_ids = self.dialogue(root)
            result = lock_creative_brief(root, self.brief(event_ids))
            self.assertEqual(result["phase"], "BIND")
            self.assertEqual(result["production_mode"], "studio")
            current = status(root)
            self.assertEqual(current["calibration_status"], "LOCKED")
            self.assertEqual(current["dialogue_rounds"], 2)
            self.assertTrue(Path(result["compiled_shot"]).is_file())

    def test_moonshot_requires_explicit_amplification_and_scope_guard(self) -> None:
        temporary, root = self.make_root()
        with temporary:
            initialize(root, "Build a game", production_mode="moonshot")
            event_ids = self.dialogue(root)
            brief = self.brief(event_ids, mode="moonshot")
            brief["moonshot"] = {"ambition_expansion": "", "scope_guard": ""}
            with self.assertRaisesRegex(OneShottedError, "ambition_expansion"):
                lock_creative_brief(root, brief)

    def test_production_gates_cannot_bypass_dialogue_lock(self) -> None:
        temporary, root = self.make_root()
        with temporary:
            initialize(root, "Build a game")
            with self.assertRaisesRegex(OneShottedError, "Lock the creative brief"):
                add_gate(root, "FLOW", "Complete flow", "The game loop completes", "lead", "verifier")
            with self.assertRaisesRegex(OneShottedError, "Use lock-brief"):
                transition(root, phase="BIND")

    def test_finalize_cannot_bypass_dialogue_lock(self) -> None:
        temporary, root = self.make_root()
        with temporary:
            initialize(root, "Build a game")
            with self.assertRaisesRegex(OneShottedError, "must be LOCKED"):
                finalize(root)

    def test_validation_rejects_tampered_question_options(self) -> None:
        temporary, root = self.make_root()
        with temporary:
            initialize(root, "Build a game")
            record_dialogue_turn(
                root,
                "model",
                "question",
                "Choose the production route.",
                effects=["clarify"],
                advances=["production_mode"],
                options=["A|Focused|Fast", "B|Studio|Polished"],
                recommended="B",
            )
            ledger = root / ".loopseed" / "one-shotted" / "dialogue.jsonl"
            event = json.loads(ledger.read_text(encoding="utf-8"))
            event["options"] = [{"id": "A", "label": "Focused", "consequence": "Fast"}]
            ledger.write_text(json.dumps(event) + "\n", encoding="utf-8")
            report = validate(root)
            self.assertFalse(report["ok"])
            self.assertTrue(any("between 2 and 4" in error for error in report["errors"]))


if __name__ == "__main__":
    unittest.main()
