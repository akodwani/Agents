from agents.consultant import ConsultingInput, generate_consulting_output, required_sections


def test_output_contains_all_required_sections():
    payload = ConsultingInput(
        situation="Revenue is flat.",
        complication="Initiatives are spread too thin.",
        question="What should we do first?",
        alternatives=("Option A", "Option B", "Option C"),
    )

    output = generate_consulting_output(payload)

    for section in required_sections():
        assert section in output


def test_decision_forcer_has_mandatory_elements():
    payload = ConsultingInput(
        situation="Customer churn increased.",
        complication="Multiple teams propose conflicting remedies.",
        question="Which path should be selected now?",
        alternatives=("Retain strategy", "Pricing strategy", "Product strategy"),
    )

    output = generate_consulting_output(payload)

    assert "Kill 2 alternatives" in output
    assert "Pick 1 path with no hedging" in output
    assert "Cost of waiting" in output
    assert "Falsifiability (what changes mind)" in output
    assert "Milestones (3 max)" in output
