def create_learning_plan(missing_skills):
    plan = []

    for skill in missing_skills:
        skill_clean = skill.strip()

        if skill_clean.lower() == "machine learning":
            plan.append(
                {
                    "skill": "Machine Learning",
                    "steps": [
                        "Learn supervised learning",
                        "Learn classification and regression",
                        "Learn model evaluation",
                        "Build one beginner ML project",
                    ],
                }
            )

        elif skill_clean.lower() == "git":
            plan.append(
                {
                    "skill": "Git",
                    "steps": [
                        "Learn Git basics",
                        "Create a GitHub repository",
                        "Practice commits and branches",
                        "Upload a project",
                    ],
                }
            )

        elif skill_clean.lower() == "tensorflow":
            plan.append(
                {
                    "skill": "TensorFlow",
                    "steps": [
                        "Learn TensorFlow basics",
                        "Build a simple neural network",
                        "Train a small model",
                        "Document the project",
                    ],
                }
            )

        elif skill_clean.lower() == "python":
            plan.append(
                {
                    "skill": "Python",
                    "steps": [
                        "Learn Python fundamentals",
                        "Practice functions and data structures",
                        "Work with files and APIs",
                        "Build a small Python project",
                    ],
                }
            )

        elif skill_clean.lower() == "java":
            plan.append(
                {
                    "skill": "Java",
                    "steps": [
                        "Learn Java fundamentals",
                        "Practice object-oriented programming",
                        "Work with collections",
                        "Build a small Java project",
                    ],
                }
            )

        else:
            plan.append(
                {
                    "skill": skill_clean,
                    "steps": [
                        f"Learn {skill_clean} fundamentals",
                        f"Practice {skill_clean}",
                        f"Build a small {skill_clean} project",
                    ],
                }
            )

    return plan