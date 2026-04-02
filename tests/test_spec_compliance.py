from src.models import Action, Observation, Reward


def test_models_required_fields():
    obs = Observation(
        email_id="id1",
        sender="a@b.com",
        subject="s",
        body="b",
        urgency=0.5,
        category="internal",
        inbox_size=5,
        time_budget_remaining=20,
        step=1,
    )
    action = Action(action_type="read", confidence=0.3)
    reward = Reward(value=0.1, breakdown={"x": 1})
    assert obs.email_id == "id1"
    assert action.is_valid_action()
    assert reward.value == 0.1
