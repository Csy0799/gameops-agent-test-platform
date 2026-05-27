import pytest

from app.core.exceptions import AppException
from app.services.probability_service import ProbabilityService


@pytest.fixture()
def service():
    return ProbabilityService()


def test_valid_probability_config_success(service):
    service.validate_probability_config(
        {"probability": 0.2, "sample_size": 1000, "tolerance": 0.01}
    )


def test_probability_less_than_zero_fails(service):
    with pytest.raises(AppException, match="probability must be between 0 and 1"):
        service.validate_probability_config({"probability": -0.1})


def test_probability_greater_than_one_fails(service):
    with pytest.raises(AppException, match="probability must be between 0 and 1"):
        service.validate_probability_config({"probability": 1.1})


def test_probability_zero_success(service):
    result = service.validate_drop_rate(probability=0, sample_size=1000)

    assert result["actual_probability"] == 0
    assert result["pass"] is True


def test_probability_one_success(service):
    result = service.validate_drop_rate(probability=1, sample_size=1000)

    assert result["actual_probability"] == 1
    assert result["pass"] is True


def test_sample_size_not_positive_fails(service):
    with pytest.raises(AppException, match="sample_size must be greater than 0"):
        service.validate_probability_config({"probability": 0.2, "sample_size": 0})


def test_tolerance_not_positive_fails(service):
    with pytest.raises(AppException, match="tolerance must be greater than 0"):
        service.validate_probability_config({"probability": 0.2, "tolerance": 0})


def test_same_seed_produces_stable_simulation_result(service):
    first = service.simulate_drop_rate(probability=0.2, sample_size=1000, seed=42)
    second = service.simulate_drop_rate(probability=0.2, sample_size=1000, seed=42)

    assert first == second


def test_different_seed_allows_different_simulation_result(service):
    first = service.simulate_drop_rate(probability=0.2, sample_size=1000, seed=42)
    second = service.simulate_drop_rate(probability=0.2, sample_size=1000, seed=43)

    assert first != second


def test_deviation_is_calculated_correctly(service):
    result = service.validate_drop_rate(probability=0.2, sample_size=1000, seed=42)

    assert result["deviation"] == abs(result["actual_probability"] - 0.2)


def test_tolerance_controls_pass_result(service):
    result = service.validate_drop_rate(probability=0.2, sample_size=1000, tolerance=0.001)

    assert result["deviation"] > 0.001
    assert result["pass"] is False


def test_low_probability_without_pity_threshold_returns_warning(service):
    warnings = service.validate_pity_rule(probability=0.005)

    assert warnings == ["low probability without pity threshold should be reviewed"]


def test_valid_pity_threshold_success(service):
    warnings = service.validate_pity_rule(probability=0.2, pity_threshold=10)

    assert warnings == []


def test_invalid_pity_threshold_fails(service):
    with pytest.raises(AppException, match="pity_threshold must be greater than 0"):
        service.validate_pity_rule(probability=0.2, pity_threshold=0)


def test_zero_probability_with_pity_threshold_returns_warning(service):
    warnings = service.validate_pity_rule(probability=0, pity_threshold=10)

    assert "pity threshold is the only acquisition path and needs review" in warnings
