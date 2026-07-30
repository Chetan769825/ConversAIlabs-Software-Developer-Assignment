import pytest
from pydantic import ValidationError

from agent.models import ExecutionPlan


def test_plan_parsing() -> None:
    plan = ExecutionPlan.model_validate({
        "requirement_understanding": "Improve search",
        "repository_understanding": "API",
        "selected_approach": "Add query filters",
        "files_to_change": [{
            "path": "app.js", "purpose": "filter", "change_type": "modify",
            "expected_effect": "search",
        }],
        "validation_steps": ["npm test"],
    })
    assert plan.files_to_change[0].change_type == "modify"


def test_invalid_change_type_fails() -> None:
    with pytest.raises(ValidationError):
        ExecutionPlan.model_validate({
            "requirement_understanding": "x", "repository_understanding": "x",
            "selected_approach": "x", "files_to_change": [{
                "path": "x", "purpose": "x", "change_type": "destroy", "expected_effect": "x"
            }], "validation_steps": [],
        })
