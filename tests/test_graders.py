from src.graders import grade_task_easy, grade_task_hard, grade_task_medium


def test_graders_range():
    traj = [
        {"email": {"urgency": 0.9, "category": "urgent_alert"}, "action": "flag", "step": 1, "time_budget": 35},
        {"email": {"urgency": 0.1, "category": "spam"}, "action": "archive", "step": 2, "time_budget": 35},
        {"email": {"urgency": 0.4, "category": "internal"}, "action": "read", "step": 3, "time_budget": 35},
    ]
    for grader in (grade_task_easy, grade_task_medium, grade_task_hard):
        score = grader(traj)
        assert 0.0 <= score <= 1.0
