import pandas as pd

data = {
    "feedback_text": [
        "The course was really well organized and resources were great, but we need a textbook for materials science.",
        "The assignments were super hard, and the grading was not clear or fair. We need a rubric.",
        "I loved the class and the teacher was super helpful!"
    ],
    "department": ["Science", "Engineering", "Business"],
    "semester": ["Spring 2024", "Spring 2024", "Fall 2023"]
}

df = pd.DataFrame(data)
df.to_csv("test_feedback.csv", index=False)
print("Created test_feedback.csv")
