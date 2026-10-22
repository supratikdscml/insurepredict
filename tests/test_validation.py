import pytest

from insurepredict.validation import validate_inputs

GOOD = {"age": 35, "gender": "Female", "bmi": 27.5, "children": 1, "smoking": "Non-smoker", "region": "Southeast"}


def test_valid_input_is_cleaned_and_typed():
    r = validate_inputs(GOOD)
    assert r.ok and not r.errors and not r.warnings
    assert r.person.to_record() == {"age": 35, "sex": "female", "bmi": 27.5, "children": 1, "smoker": "no", "region": "southeast"}


def test_missing_fields_reported_together():
    r = validate_inputs({**GOOD, "age": None, "region": None})
    assert not r.ok and "Age" in r.errors[0] and "Region" in r.errors[0]


@pytest.mark.parametrize("field,value", [("age", 17), ("age", 101), ("age", 35.5), ("bmi", 5), ("bmi", 90),
                                         ("children", -1), ("children", 11), ("children", 1.5)])
def test_out_of_range_or_fractional_values_rejected(field, value):
    assert not validate_inputs({**GOOD, field: value}).ok


@pytest.mark.parametrize("field,value", [("gender", "Other"), ("smoking", "Maybe"), ("region", "Mars")])
def test_unknown_categories_rejected(field, value):
    assert not validate_inputs({**GOOD, field: value}).ok


def test_values_outside_training_range_give_warning_not_error():
    r = validate_inputs({**GOOD, "age": 80})
    assert r.ok and any("outside the range" in w for w in r.warnings)
