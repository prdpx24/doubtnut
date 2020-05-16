from django.db import models

from .utils import extract_text_from_image, bisect_extracted_question


def user_asked_question_image_path(instance, filename):
    question_id = instance.question_id
    return "questions/{}/{}".format(question_id, filename)


class Tag(models.Model):
    name = models.CharField(max_length=20, blank=False, null=False)

    def __str__(self):
        return name


class Question(models.Model):
    title = models.CharField(max_length=500, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    tags = models.ManyToManyField(Tag)
    created_by = models.ForeignKey(
        "users.User", blank=False, null=False, on_delete=models.CASCADE
    )

    def __str__(self):
        return "{} - {}".format(self.title, self.created_by.username)


class UserAskedQuestion(models.Model):
    image = models.ImageField(upload_to=user_asked_question_image_path)
    question = models.ForeignKey(
        Question, blank=True, null=True, on_delete=models.CASCADE
    )

    def __str__(self):
        return "{}".format(self.question)
