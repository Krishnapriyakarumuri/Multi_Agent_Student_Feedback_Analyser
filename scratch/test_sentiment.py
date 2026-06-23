from transformers import pipeline

model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
print(f"Loading {model_name}...")
pipe = pipeline("sentiment-analysis", model=model_name)

examples = [
    "I absolutely love this course, it is amazing!",
    "This is the worst experience I have ever had. I hate it.",
    "The course is okay, nothing special but fine.",
]

for text in examples:
    result = pipe(text)[0]
    print(f"Text: {text}")
    print(f"Result: {result}")
