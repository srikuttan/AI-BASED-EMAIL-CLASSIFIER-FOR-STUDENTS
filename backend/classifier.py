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
            ("Submit the chemistry record before 5 PM", "Assignments"),
            ("Upload your project report on the portal", "Assignments"),
            ("Final year project presentation next week", "Assignments"),
            ("Complete the coding assignment in Python", "Assignments"),
            ("Internal marks will be based on assignment submission", "Assignments"),
            ("Please finish the lab manual and submit", "Assignments"),
            ("Case study analysis due by tomorrow", "Assignments"),
            ("Prepare PPT for seminar evaluation", "Assignments"),
            ("Assignment 3 submission deadline extended", "Assignments"),
            ("Submit your internship report by Friday", "Assignments"),
            ("Database mini project submission", "Assignments"),
            ("AI model implementation task assigned", "Assignments"),
            ("Complete Unit 4 homework questions", "Assignments"),
            ("Research paper review submission", "Assignments"),
            ("Group project documentation required", "Assignments"),
            
            
            ("Holiday declared on Monday", "Notices"),
            ("Exam schedule for semester 4", "Notices"),
            ("Library books renewal reminder", "Notices"),
            ("Guest lecture on AI this week", "Notices"),
            ("Campus maintenance scheduled", "Notices"),
            ("Midterm exams start from March 10", "Notices"),
            ("College will remain closed tomorrow", "Notices"),
            ("Workshop on cybersecurity this Saturday", "Notices"),
            ("Results for semester 3 published", "Notices"),
            ("Timetable updated on website", "Notices"),
            ("Bus timings changed for this week", "Notices"),
            ("Fee payment deadline reminder", "Notices"),
            ("Sports day scheduled next month", "Notices"),
            ("New circular from university", "Notices"),
            ("Classroom shifted to Block B", "Notices"),
            ("Attendance shortage notice", "Notices"),
            ("Practical exam schedule announced", "Notices"),
            ("Guest speaker session on machine learning", "Notices"),
            ("Library will be closed for maintenance", "Notices"),
            ("Scholarship application deadline approaching", "Notices"),
            
            
            ("Hey, are we meeting for coffee?", "Personal"),
            ("Happy birthday! Have a great day", "Personal"),
            ("Can you send me the notes?", "Personal"),
            ("Lets go for a movie", "Personal"),
            ("How was your trip?", "Personal"),
            ("Are you coming to college today?", "Personal"),
            ("Let's study together for exams", "Personal"),
            ("Did you complete the assignment?", "Personal"),
            ("Meet me at the cafeteria at 4", "Personal"),
            ("Thanks for your help yesterday", "Personal"),
            ("Call me when you are free", "Personal"),
            ("Can you share the class notes?", "Personal"),
            ("We are planning a trip this weekend", "Personal"),
            ("Happy anniversary!", "Personal"),
            ("Best wishes for your presentation", "Personal"),
            ("How are your preparations going?", "Personal"),
            ("Let's revise the syllabus together", "Personal"),
            ("Are you attending the workshop?", "Personal"),
            ("Send me the lab experiment readings", "Personal"),
            ("Congrats on your achievement!", "Personal"),
            
            
            ("You won a lottery! Click here", "Spam"),
            ("Limited time offer, buy now", "Spam"),
            ("Verify your bank account immediately", "Spam"),
            ("Cheap pills for sale", "Spam"),
            ("Claim your free gift card now", "Spam"),
            ("You have been selected for a cash prize", "Spam"),
            ("Act now to receive exclusive bonus", "Spam"),
            ("Your account has been compromised click here", "Spam"),
            ("Earn money from home easily", "Spam"),
            ("Hot deals available today only", "Spam"),
            ("Free cryptocurrency investment opportunity", "Spam"),
            ("Get rich quick scheme", "Spam"),
            ("Lowest prices guaranteed buy now", "Spam"),
            ("This is not a scam trust us", "Spam"),
            ("Immediate response required verify details", "Spam"),
            ("Click to win iPhone now", "Spam"),
            ("Congratulations you won 1 million dollars", "Spam"),
            ("Limited stock order today", "Spam"),
            ("Exclusive loan approval offer", "Spam"),
            
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
