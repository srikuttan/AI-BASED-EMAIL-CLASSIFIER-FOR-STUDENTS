import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
import os

class EmailClassifier:
    def __init__(self):
        self.model = None
        self.categories = ["Assignments", "Notices", "Personal", "Spam"]
        self.train_model()

    def train_model(self):
        # Synthetic dataset for student context
        data = [
            ("Submit your math assignment by Friday", "Assignments"),
            ("Physics lab record due tomorrow", "Assignments"),
            ("History essay submission link", "Assignments"),
            ("Project deadline extended", "Assignments"),
            ("Homework for chapter 5", "Assignments"),
            
            ("Holiday declared on Monday", "Notices"),
            ("Exam schedule for semester 4", "Notices"),
            ("Library books renewal reminder", "Notices"),
            ("Guest lecture on AI this week", "Notices"),
            ("Campus maintenance scheduled", "Notices"),
            
            ("Hey, are we meeting for coffee?", "Personal"),
            ("Happy birthday! Have a great day", "Personal"),
            ("Can you send me the notes?", "Personal"),
            ("Lets go for a movie", "Personal"),
            ("How was your trip?", "Personal"),
            
            ("You won a lottery! Click here", "Spam"),
            ("Limited time offer, buy now", "Spam"),
            ("Verify your bank account immediately", "Spam"),
            ("Cheap pills for sale", "Spam"),
            ("Congratulations, you are a winner", "Spam")
        ]
        
        df = pd.DataFrame(data, columns=["text", "label"])
        
        self.model = make_pipeline(TfidfVectorizer(), LogisticRegression())
        self.model.fit(df["text"], df["label"])
        print("Model trained on synthetic data.")

    def predict(self, subject, body):
        if not self.model:
            self.train_model()
        
        full_text = f"{subject} {body}"
        prediction = self.model.predict([full_text])[0]
        return prediction

classifier = EmailClassifier()
