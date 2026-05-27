"""Example: Instrumenting a simple AI agent with Beacon."""
from beacon import trace
import time
import random

@trace(agent_id="email-classifier", api_url="http://localhost:8000")
def classify_email(subject: str, body: str) -> str:
    """Classify an email as spam or not spam."""
    time.sleep(0.5 + random.random())
    if random.random() < 0.1:
        raise ValueError("LLM timeout")
    return "spam" if "urgent" in subject.lower() else "not_spam"

if __name__ == "__main__":
    emails = [
        ("Meeting tomorrow", "Let's sync at 2pm"),
        ("URGENT: Action required", "Click here now"),
        ("Weekly report", "Here is the summary"),
    ]
    for subject, body in emails:
        try:
            result = classify_email(subject, body)
            print(f"  {subject} -> {result}")
        except Exception as e:
            print(f"  {subject} -> ERROR: {e}")
    print("\nDone. Check http://localhost:3000 for traces.")
