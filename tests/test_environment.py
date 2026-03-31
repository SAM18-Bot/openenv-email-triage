from src.environment import EmailTriageOpenEnv


def test_reset_and_step():
    env = EmailTriageOpenEnv()
    obs = env.reset(seed=1)
    assert obs.email_id
    next_obs, reward, done, info = env.step({"action_type": "read", "confidence": 0.8})
    assert isinstance(done, bool)
    assert "step" in reward.breakdown
    assert "queue_size" in info
    assert next_obs.step >= 1
