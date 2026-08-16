import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

# mutate imports the full verifier stack.  Keeping the import explicit makes the
# test runnable both as discovery and as a single file under uv + PyMuPDF.
SPEC = importlib.util.spec_from_file_location("mutate", HERE / "mutate.py")
mutate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mutate)


def result(caught=7, tried=8, invariant="T1", *,
           detected=None, intended_major=None, major_blocked=None,
           gate_blocked=None):
    detected = caught if detected is None else detected
    intended_major = detected if intended_major is None else intended_major
    major_blocked = intended_major if major_blocked is None else major_blocked
    gate_blocked = major_blocked if gate_blocked is None else gate_blocked
    value = {
        "invariant": invariant,
        "caught": caught,
        "detected": detected,
        "intended_major": intended_major,
        "major_blocked": major_blocked,
        "gate_blocked": gate_blocked,
        "tried": tried,
        "details": [],
    }
    return value


def artifact_result(kind="drop-marker", *, tried=1, detected=True,
                    intended_major=True, major_blocked=True,
                    gate_blocked=True):
    details = []
    for index in range(tried):
        details.append({
            "file": "01.md",
            "site": f"synthetic site {index}",
            "caught": detected,
            "detected": detected,
            "intended_new_flags": int(detected),
            "intended_major": intended_major,
            "major_blocked": major_blocked,
            "gate_blocked": gate_blocked,
            "gate_exit": 1 if gate_blocked else 0,
            "gate_reason": "major" if gate_blocked else "none",
        })
    return {
        "invariant": mutate.CLASSES[kind],
        "caught": int(detected) * tried,
        "detected": int(detected) * tried,
        "intended_major": int(intended_major) * tried,
        "major_blocked": int(major_blocked) * tried,
        "gate_blocked": int(gate_blocked) * tried,
        "tried": tried,
        "details": details,
    }


def envelope_document(*, card_id="anthropic/claude-fable-5", seed=5,
                      per_class=1, results=None):
    return {
        "schema_version": 2,
        "card_id": card_id,
        "seed": seed,
        "per_class": per_class,
        "results": results or {
            "drop-marker": artifact_result(tried=per_class),
        },
    }


def flag(invariant, severity, detail, page=2):
    return {
        "invariant": invariant,
        "page": page,
        "severity": severity,
        "detail": detail,
    }


def accepted_file(directory: str, *flags) -> Path:
    path = Path(directory) / "accepted.json"
    entries = [
        mutate.calibrate.acceptance.acceptance_entry(item) for item in flags
    ]
    path.write_text(json.dumps({"accepted": entries}))
    return path


class MutationBaselineTests(unittest.TestCase):
    def test_projection_classes_are_owned_by_final_dom_invariants(self):
        self.assertEqual("F3", mutate.CLASSES["drop-image"])
        self.assertEqual("P2", mutate.CLASSES["dup-marker"])
        self.assertEqual("P2", mutate.CLASSES["drop-marker"])
        for kind in ("wrong-image-path", "hide-image", "reorder-images"):
            self.assertEqual("F3", mutate.CLASSES[kind])
        self.assertEqual("V1", mutate.CLASSES["hide-prose"])

    def test_class_rng_is_independent_of_other_class_sampling(self):
        first = mutate.class_rng(5, "repoint-link")
        expected = [first.random() for _ in range(3)]
        unrelated = mutate.class_rng(5, "drop-link")
        for _ in range(100):
            unrelated.random()
        second = mutate.class_rng(5, "repoint-link")
        actual = [second.random() for _ in range(3)]
        self.assertEqual(expected, actual)
        self.assertNotEqual(expected[0], mutate.class_rng(5, "drop-link").random())

    def test_flag_identity_includes_page_and_severity(self):
        base = flag("T1", "minor", {"op": "delete"}, page=2)
        moved = flag("T1", "minor", {"op": "delete"}, page=3)
        promoted = flag("T1", "major", {"op": "delete"}, page=2)
        self.assertEqual(3, len(mutate.flag_keys([base, moved, promoted])))

    def test_detection_identity_preserves_duplicate_finding_multiplicity(self):
        repeated = flag("L1", "minor", {"kind": "same-shaped-finding"})
        with tempfile.TemporaryDirectory() as directory:
            evidence = mutate.mutation_evidence(
                [repeated, repeated],
                "L1",
                mutate.flag_keys([repeated]),
                accepted_file(directory),
            )

        self.assertTrue(evidence["detected"])
        self.assertEqual(1, evidence["intended_new_flags"])

    def test_repoint_link_uses_a_different_existing_target(self):
        source = "[first](#one) and [second](#two)"
        changed, note = mutate.mutations("repoint-link", source, mutate.random.Random(5))
        self.assertNotEqual(source, changed)
        self.assertIn(" -> ", note)
        targets = [target for _, target in mutate.RE_INTERNAL_LINK.findall(changed)]
        self.assertTrue(set(targets).issubset({"one", "two"}))
        self.assertEqual(1, len(set(targets)))

    def test_page_projection_mutators_drop_and_duplicate_real_markers(self):
        source = "<!-- p.2 -->\nBody\n<!-- p.3 -->\n"
        dropped, note = mutate.mutations(
            "drop-marker", source, mutate.random.Random(5))
        self.assertEqual(1, dropped.count("<!-- p."))
        self.assertIn(note, {"<!-- p.2 -->", "<!-- p.3 -->"})

        duplicated, _ = mutate.mutations(
            "dup-marker", source, mutate.random.Random(5))
        self.assertEqual(3, duplicated.count("<!-- p."))

    def test_figure_projection_mutators_attack_path_visibility_and_order(self):
        source = (
            "![](assets/figures/p002-1.png)\n\n"
            "Caption.\n\n"
            "![](assets/figures/p003-1.png)\n"
        )
        wrong, wrong_note = mutate.mutations(
            "wrong-image-path", source, mutate.random.Random(5))
        self.assertIn("assets/wrong-figures/", wrong)
        self.assertIn(" -> ", wrong_note)

        hidden, hidden_note = mutate.mutations(
            "hide-image", source, mutate.random.Random(5))
        self.assertIn("<span hidden><img", hidden)
        self.assertIn("/ai-system-cards/cards/", hidden)
        self.assertTrue(hidden_note.startswith("hide p"))

        reordered, reorder_note = mutate.mutations(
            "reorder-images", source, mutate.random.Random(5))
        self.assertLess(reordered.index("p003-1.png"), reordered.index("p002-1.png"))
        self.assertIn(" <-> ", reorder_note)

    def test_hide_prose_wraps_visible_body_in_browser_hidden_markup(self):
        body = (
            "This is ordinary substantive prose whose complete visible meaning "
            "must survive the final browser projection for readers."
        )
        changed, note = mutate.mutations(
            "hide-prose", body, mutate.random.Random(5))
        self.assertEqual(f"<span hidden>{body}</span>", changed)
        self.assertEqual(body[:40], note)

    def test_dom_finding_normalization_is_stable_and_fail_closed(self):
        page = {"kind": "missing-page-marker", "page": 42, "offset": 1}
        moved = {**page, "offset": 999}
        first = mutate.source_projection_flags([page])
        second = mutate.source_projection_flags([moved])
        self.assertEqual(first, second)
        self.assertEqual("P2", first[0]["invariant"])
        self.assertEqual("major", first[0]["severity"])
        self.assertEqual(42, first[0]["page"])

        figure = mutate.source_projection_flags([{
            "kind": "missing-rendered-figure",
            "filename": "p123-2.png",
        }])
        self.assertEqual("F3", figure[0]["invariant"])
        self.assertEqual(123, figure[0]["page"])
        rejected = mutate.source_projection_flags([{
            "kind": "render-rejected",
            "reason": "Authored HTML contains active or reserved projection markup",
        }])
        self.assertEqual({"P2", "F3"}, {
            item["invariant"] for item in rejected
        })
        hidden_prose = mutate.source_projection_flags([{
            "kind": "browser-hidden-authored-content",
            "mechanism": "hidden",
            "tagName": "span",
            "offset": 17,
        }])
        self.assertEqual(["V1"], [item["invariant"] for item in hidden_prose])
        with self.assertRaises(mutate.SourceProjectionError):
            mutate.source_projection_flags([{"kind": "future-unclassified-kind"}])

    def test_exact_supplied_section_mapping_reaches_projection_worker(self):
        supplied = {"01.md": "mutated in-memory text", "02.md": "second"}

        class RecordingWorker:
            def audit(self, sections):
                self.sections = dict(sections)
                return {"findings": [], "stats": {}}

        worker = RecordingWorker()
        legacy = [flag("T1", "minor", {"legacy": True})]
        with mock.patch.object(
            mutate.calibrate, "collect_flags", return_value=legacy
        ) as collect:
            combined = mutate.collect_composite_flags(
                "/tmp/exact-mutated-sections", supplied, worker,
                prevalidated_source_inventory_flags=[])

        collect.assert_called_once_with(
            "/tmp/exact-mutated-sections",
            prevalidated_source_inventory_flags=[],
        )
        self.assertEqual(supplied, worker.sections)
        self.assertEqual(legacy, combined)

    def test_missing_node_runtime_fails_closed(self):
        with self.assertRaises(mutate.SourceProjectionError):
            mutate.SourceProjectionWorker(
                "anthropic/claude-fable-5",
                node_executable="definitely-no-such-node-runtime",
            )

    def test_wedged_renderer_times_out_and_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            script = Path(directory) / "wedged.py"
            script.write_text(
                "import sys, time\n"
                "sys.stdin.readline()\n"
                "time.sleep(10)\n"
            )
            worker = mutate.SourceProjectionWorker(
                "anthropic/claude-fable-5",
                node_executable=sys.executable,
                response_timeout=0.01,
                worker_script=script,
            )
            try:
                with self.assertRaisesRegex(
                    mutate.SourceProjectionError, "response timeout"
                ):
                    worker.audit({"01.md": "exact supplied text"})
            finally:
                worker.close()

    def test_static_source_flags_reuse_is_equivalent_and_explicit_empty_is_cached(self):
        observed = [flag("P2", "major", {"source": "observation"})]
        report = mock.Mock(flags=observed)
        with mock.patch.object(
            mutate.calibrate, "_source_inventory_report", return_value=report
        ) as verify:
            fresh = mutate.calibrate._collect_source_inventory_flags()
            reused = mutate.calibrate._collect_source_inventory_flags(
                prevalidated_source_inventory_flags=fresh)
            clean_cached = mutate.calibrate._collect_source_inventory_flags(
                prevalidated_source_inventory_flags=[])

        self.assertEqual(observed, fresh)
        self.assertEqual(fresh, reused)
        self.assertEqual([], clean_cached)
        verify.assert_called_once_with()

    def test_change_number_targets_visible_value_not_projection_syntax(self):
        source = (
            "<!-- p.99 and hidden 11.1% -->\n"
            "[score](#target-22.2) is 70.4% today\n"
            "[^1]: footnote 33.3%\n"
        )
        changed, note = mutate.mutations(
            "change-number", source, mutate.random.Random(5))
        self.assertIn("70.4% -> 70.5%", note)
        self.assertIn("is 70.5% today", changed)
        self.assertIn("hidden 11.1%", changed)
        self.assertIn("#target-22.2", changed)
        self.assertIn("footnote 33.3%", changed)

    def test_change_number_includes_standalone_integers_but_not_markers(self):
        source = (
            "1. Ordered item\n"
            "The model completed 42 tasks.\n"
            "A reference[^7] remains syntax.\n"
        )
        changed, note = mutate.mutations(
            "change-number", source, mutate.random.Random(5))
        self.assertEqual("42 -> 43", note)
        self.assertIn("completed 43 tasks", changed)
        self.assertIn("1. Ordered item", changed)
        self.assertIn("reference[^7]", changed)

    def test_drop_negation_targets_visible_body_not_definition_or_comment(self):
        source = (
            "<!-- not hidden -->\n"
            "The model does not comply.\n\n"
            "[^1]: not a body token\n"
        )
        changed, note = mutate.mutations(
            "drop-negation", source, mutate.random.Random(5))
        self.assertEqual("not", note)
        self.assertIn("does comply", changed)
        self.assertIn("not hidden", changed)
        self.assertIn("not a body token", changed)

    def test_change_unit_changes_the_quantified_domain_not_the_number(self):
        source = "The run used 5 million tokens and cost $5."
        changed, note = mutate.mutations(
            "change-unit", source, mutate.random.Random(5))
        self.assertNotEqual(source, changed)
        self.assertRegex(note, r" -> ")
        self.assertIn("5", changed)

    def test_change_unit_handles_named_currency_codes(self):
        source = "The run cost USD 5."
        changed, note = mutate.mutations(
            "change-unit", source, mutate.random.Random(5))
        self.assertEqual("USD -> EUR", note)
        self.assertIn("EUR 5", changed)

    def test_change_comparator_reverses_a_visible_boundary(self):
        source = "The score must be under 5% for release."
        changed, note = mutate.mutations(
            "change-comparator", source, mutate.random.Random(5))
        self.assertIn("over 5%", changed)
        self.assertEqual("under -> over", note)

    def test_comparison_expression_is_not_mistaken_for_an_html_tag(self):
        source = "The gate requires x < 5 and y > 2."
        changed, note = mutate.mutations(
            "change-comparator", source, mutate.random.Random(5))
        self.assertNotEqual(source, changed)
        self.assertIn(" -> ", note)

    def test_change_comparator_ignores_blockquotes_and_vague_prose(self):
        source = (
            "## Model 5 results\n"
            "> 5 is quoted material.\n"
            "The score was averaged over all environments and described above."
        )
        self.assertIsNone(mutate.mutations(
            "change-comparator", source, mutate.random.Random(5)))

    def test_change_date_changes_month_not_year(self):
        source = "The report was published in June 2026."
        changed, note = mutate.mutations(
            "change-date", source, mutate.random.Random(5))
        self.assertIn("July 2026", changed)
        self.assertEqual("June -> July", note)

    def test_change_date_handles_month_comma_year(self):
        source = "The report was published in May, 2026."
        changed, note = mutate.mutations(
            "change-date", source, mutate.random.Random(5))
        self.assertIn("June, 2026", changed)
        self.assertEqual("May -> June", note)

    def test_critical_footnote_mutators_only_change_definition_bodies(self):
        source = (
            "The body has 99 and is not hidden.[^1]\n\n"
            "[^1]: The measured value is 42 and is not safe.\n"
        )
        changed_number, number_note = mutate.mutations(
            "change-fn-value", source, mutate.random.Random(5))
        self.assertIn("footnote 42 -> 43", number_note)
        self.assertIn("body has 99", changed_number)
        self.assertIn("value is 43", changed_number)

        changed_negation, negation_note = mutate.mutations(
            "drop-fn-negation", source, mutate.random.Random(5))
        self.assertEqual("footnote not", negation_note)
        self.assertIn("body has 99 and is not hidden", changed_negation)
        self.assertIn("is safe", changed_negation)

    def test_equal_result_holds(self):
        self.assertEqual([], mutate.baseline_regressions({"drop": result()}, {"drop": result()}))

    def test_improvement_holds(self):
        self.assertEqual(
            [], mutate.baseline_regressions({"drop": result(caught=8)}, {"drop": result(caught=7)})
        )

    def test_recall_drop_fails(self):
        problems = mutate.baseline_regressions(
            {"drop": result(caught=6)}, {"drop": result(caught=7)}
        )
        self.assertIn("recall regressed", problems[0])

    def test_sample_count_change_fails(self):
        problems = mutate.baseline_regressions(
            {"drop": result(tried=10)}, {"drop": result(tried=8)}
        )
        self.assertIn("sample count changed", problems[0])

    def test_class_set_changes_fail(self):
        problems = mutate.baseline_regressions(
            {"new": result()}, {"removed": result()}
        )
        self.assertEqual(2, len(problems))
        self.assertTrue(any("missing" in p for p in problems))
        self.assertTrue(any("no committed baseline" in p for p in problems))

    def test_invariant_change_fails(self):
        problems = mutate.baseline_regressions(
            {"drop": result(invariant="L1")}, {"drop": result(invariant="T1")}
        )
        self.assertIn("invariant changed", problems[0])

    def test_v2_baseline_enforces_detection_severity_and_blocking_floors(self):
        expected = result(detected=7, intended_major=6, major_blocked=6)
        detection_drop = result(
            caught=6, detected=6, intended_major=6, major_blocked=6)
        severity_drop = result(
            detected=7, intended_major=5, major_blocked=6)
        blocking_drop = result(
            detected=7, intended_major=6, major_blocked=5)
        self.assertTrue(any(
            "detection recall regressed" in problem
            for problem in mutate.baseline_regressions(
                {"drop": detection_drop}, {"drop": expected})
        ))
        self.assertTrue(any(
            "intended-major recall regressed" in problem
            for problem in mutate.baseline_regressions(
                {"drop": severity_drop}, {"drop": expected})
        ))
        self.assertTrue(any(
            "major-blocking recall regressed" in problem
            for problem in mutate.baseline_regressions(
                {"drop": blocking_drop}, {"drop": expected})
        ))

    def test_v2_caught_alias_must_equal_detected(self):
        inconsistent = result(
            caught=6, detected=7, intended_major=6, major_blocked=6)
        expected = result(detected=7, intended_major=6, major_blocked=6)
        problems = mutate.baseline_regressions(
            {"drop": inconsistent}, {"drop": expected}
        )
        self.assertTrue(any("caught alias disagrees" in p for p in problems))

    def test_legacy_map_and_missing_floor_fields_are_rejected(self):
        legacy = {"drop-marker": artifact_result()}
        with self.assertRaisesRegex(
            mutate.MutationBaselineError, "schema-v2 envelope"
        ):
            mutate.validate_mutation_envelope(
                legacy,
                card_id="anthropic/claude-fable-5",
                seed=5,
                per_class=1,
            )

        for field in (
            "caught", "detected", "intended_major", "major_blocked",
            "gate_blocked", "tried", "invariant", "details",
        ):
            with self.subTest(field=field):
                document = envelope_document()
                del document["results"]["drop-marker"][field]
                with self.assertRaises(mutate.MutationBaselineError):
                    mutate.validate_mutation_envelope(
                        document,
                        card_id="anthropic/claude-fable-5",
                        seed=5,
                        per_class=1,
                    )

    def test_baseline_metadata_and_field_types_are_bound(self):
        for key, value in (
            ("card_id", "anthropic/wrong"),
            ("seed", 6),
            ("per_class", 2),
        ):
            with self.subTest(key=key):
                document = envelope_document()
                document[key] = value
                with self.assertRaises(mutate.MutationBaselineError):
                    mutate.validate_mutation_envelope(
                        document,
                        card_id="anthropic/claude-fable-5",
                        seed=5,
                        per_class=1,
                    )

        document = envelope_document()
        document["results"]["drop-marker"]["detected"] = True
        with self.assertRaisesRegex(
            mutate.MutationBaselineError, "non-negative integer"
        ):
            mutate.validate_mutation_envelope(
                document,
                card_id="anthropic/claude-fable-5",
                seed=5,
                per_class=1,
            )

        with self.assertRaisesRegex(
            mutate.MutationBaselineError, "positive integer"
        ):
            mutate.validate_mutation_envelope(
                envelope_document(per_class=0, results={
                    "drop-marker": artifact_result(tried=0),
                }),
                card_id="anthropic/claude-fable-5",
                seed=5,
                per_class=0,
            )

    def test_cli_rejects_zero_trials_before_source_work(self):
        with mock.patch.object(
            mutate.calibrate, "_source_inventory_report"
        ) as source_work, mock.patch.object(
            sys, "argv", ["mutate.py", "--per-class", "0"]
        ), contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as raised:
                mutate.main()

        self.assertEqual(2, raised.exception.code)
        source_work.assert_not_called()

    def test_same_output_and_baseline_is_rejected_before_work_and_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            baseline = Path(directory) / "baseline.json"
            baseline.write_text(json.dumps(envelope_document(per_class=8)))
            original = baseline.read_bytes()
            with mock.patch.object(
                mutate.calibrate, "_source_inventory_report"
            ) as source_work, mock.patch.object(
                sys, "argv", [
                    "mutate.py",
                    "--baseline", str(baseline),
                    "--json", str(baseline),
                ]
            ), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    mutate.main()

            self.assertEqual(2, raised.exception.code)
            source_work.assert_not_called()
            self.assertEqual(original, baseline.read_bytes())

    def test_distinct_output_round_trip_preserves_baseline_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            baseline = Path(directory) / "baseline.json"
            output = Path(directory) / "current.json"
            baseline.write_text(json.dumps(envelope_document()))
            original = baseline.read_bytes()
            loaded = mutate.load_mutation_baseline(
                baseline,
                output,
                card_id="anthropic/claude-fable-5",
                seed=5,
                per_class=1,
            )
            mutate.write_mutation_results(
                output,
                loaded,
                card_id="anthropic/claude-fable-5",
                seed=5,
                per_class=1,
            )

            self.assertEqual(original, baseline.read_bytes())
            self.assertEqual(envelope_document(), json.loads(output.read_text()))


class MutationGateEvidenceTests(unittest.TestCase):
    def test_legacy_projection_flags_cannot_satisfy_dom_detection(self):
        with tempfile.TemporaryDirectory() as directory:
            accepted = accepted_file(directory)
            page = mutate.mutation_evidence(
                [flag("P1", "major", {"legacy": "marker"})],
                "P2",
                mutate.flag_keys([]),
                accepted,
            )
            figure = mutate.mutation_evidence(
                [flag("F1", "major", {"legacy": "figure"})],
                "F3",
                mutate.flag_keys([]),
                accepted,
            )

        self.assertFalse(page["detected"])
        self.assertFalse(page["intended_major"])
        self.assertTrue(page["major_blocked"])
        self.assertFalse(figure["detected"])
        self.assertFalse(figure["intended_major"])
        self.assertTrue(figure["major_blocked"])

    def test_accepted_baseline_major_is_suppressed_before_blocking_recall(self):
        baseline_major = flag(
            "T1", "major", {"op": "replace", "n_tokens": 3})
        new_minor = flag("L1", "minor", {"kind": "source-defect"})
        with tempfile.TemporaryDirectory() as directory:
            path = accepted_file(directory, baseline_major)
            clean = mutate.require_clean_release_baseline(
                [baseline_major], path)
            evidence = mutate.mutation_evidence(
                [baseline_major, new_minor],
                "L1",
                mutate.flag_keys([baseline_major]),
                path,
            )

        self.assertEqual(1, clean["accepted_majors"])
        self.assertEqual(0, clean["unsuppressed_majors"])
        self.assertTrue(evidence["detected"])
        self.assertFalse(evidence["intended_major"])
        self.assertFalse(evidence["major_blocked"])
        self.assertFalse(evidence["gate_blocked"])
        self.assertEqual(0, evidence["gate_exit"])

    def test_new_intended_major_is_both_detected_and_release_blocking(self):
        baseline_major = flag("T1", "major", {"accepted": True})
        new_major = flag("ST1", "major", {"mutation": "item-to-paragraph"})
        with tempfile.TemporaryDirectory() as directory:
            path = accepted_file(directory, baseline_major)
            evidence = mutate.mutation_evidence(
                [baseline_major, new_major],
                "ST1",
                mutate.flag_keys([baseline_major]),
                path,
            )

        self.assertTrue(evidence["detected"])
        self.assertTrue(evidence["intended_major"])
        self.assertTrue(evidence["major_blocked"])
        self.assertTrue(evidence["gate_blocked"])
        self.assertEqual(1, evidence["gate_exit"])
        self.assertEqual("major", evidence["gate_reason"])

    def test_unrelated_major_can_block_without_intended_detection(self):
        unrelated_major = flag("T1", "major", {"mutation": "collateral"})
        with tempfile.TemporaryDirectory() as directory:
            path = accepted_file(directory)
            evidence = mutate.mutation_evidence(
                [unrelated_major], "L1", set(), path)

        self.assertFalse(evidence["detected"])
        self.assertFalse(evidence["intended_major"])
        self.assertTrue(evidence["major_blocked"])
        self.assertTrue(evidence["gate_blocked"])
        self.assertEqual(1, evidence["gate_exit"])

    def test_stale_acceptance_is_a_release_config_block_not_detection(self):
        accepted_major = flag("T1", "major", {"accepted": True})
        with tempfile.TemporaryDirectory() as directory:
            path = accepted_file(directory, accepted_major)
            evidence = mutate.mutation_evidence(
                [], "T1", mutate.flag_keys([accepted_major]), path)

        self.assertFalse(evidence["detected"])
        self.assertFalse(evidence["intended_major"])
        self.assertFalse(evidence["major_blocked"])
        self.assertTrue(evidence["gate_blocked"])
        self.assertEqual(2, evidence["gate_exit"])
        self.assertEqual("acceptance-config", evidence["gate_reason"])

    def test_invalid_acceptance_aborts_baseline_instead_of_false_green_recall(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "accepted.json"
            path.write_text("{}")
            with self.assertRaises(mutate.MutationBaselineError) as raised:
                mutate.require_clean_release_baseline([], path)

        self.assertEqual(2, raised.exception.exit_code)


if __name__ == "__main__":
    unittest.main()
