from django.db import models

class Subject(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class QuestionAnswer(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    questions_json = models.TextField()
    answers_json = models.TextField()

    def __str__(self):
        return f"Questions and Answers for {self.subject.name}"
