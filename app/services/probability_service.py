import random
from typing import Any, Dict, List, Optional

from app.core.exceptions import AppException


class ProbabilityService:
    def validate_probability_config(self, config: Dict[str, Any]) -> None:
        probability = config.get("probability")
        sample_size = config.get("sample_size", 100000)
        tolerance = config.get("tolerance", 0.01)
        pity_threshold = config.get("pity_threshold")

        if probability is None:
            raise AppException(message="probability is required", code=400)
        if probability < 0 or probability > 1:
            raise AppException(message="probability must be between 0 and 1", code=400)
        if sample_size <= 0:
            raise AppException(message="sample_size must be greater than 0", code=400)
        if tolerance <= 0:
            raise AppException(message="tolerance must be greater than 0", code=400)
        if pity_threshold is not None and pity_threshold <= 0:
            raise AppException(message="pity_threshold must be greater than 0", code=400)

    def simulate_drop_rate(
        self,
        probability: float,
        sample_size: int = 100000,
        seed: int = 42,
    ) -> float:
        if probability == 0:
            return 0.0
        if probability == 1:
            return 1.0

        rng = random.Random(seed)
        hit_count = 0
        for _ in range(sample_size):
            if rng.random() < probability:
                hit_count += 1
        return hit_count / sample_size

    def validate_drop_rate(
        self,
        probability: float,
        sample_size: int = 100000,
        tolerance: float = 0.01,
        seed: int = 42,
    ) -> Dict[str, Any]:
        actual_probability = self.simulate_drop_rate(
            probability=probability,
            sample_size=sample_size,
            seed=seed,
        )
        deviation = abs(actual_probability - probability)

        return {
            "expected_probability": probability,
            "actual_probability": actual_probability,
            "deviation": deviation,
            "sample_size": sample_size,
            "tolerance": tolerance,
            "pass": deviation <= tolerance,
            "warnings": [],
        }

    def validate_pity_rule(
        self,
        probability: float,
        pity_threshold: Optional[int] = None,
    ) -> List[str]:
        if pity_threshold is not None and pity_threshold <= 0:
            raise AppException(message="pity_threshold must be greater than 0", code=400)

        warnings = []
        if probability < 0.01 and pity_threshold is None:
            warnings.append("low probability without pity threshold should be reviewed")
        if probability == 0 and pity_threshold is not None:
            warnings.append("pity threshold is the only acquisition path and needs review")
        return warnings

    def validate_probability(self, config: Dict[str, Any]) -> Dict[str, Any]:
        self.validate_probability_config(config)
        result = self.validate_drop_rate(
            probability=config["probability"],
            sample_size=config.get("sample_size", 100000),
            tolerance=config.get("tolerance", 0.01),
            seed=config.get("seed", 42),
        )
        result["warnings"] = self.validate_pity_rule(
            probability=config["probability"],
            pity_threshold=config.get("pity_threshold"),
        )
        return result


probability_service = ProbabilityService()
