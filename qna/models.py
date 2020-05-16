from django.db import models

from .utils import extract_text_from_image, bisect_extracted_question


def user_asked_question_image_path(instance, filename):
    question_id = instance.question_id
    return "questions/{}/{}".format(question_id, filename)


class Tag(models.Model):
    name = models.CharField(max_length=20, blank=False, null=False)

    def __str__(self):
        return self.name


class Question(models.Model):
    title = models.CharField(max_length=500, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    tags = models.ManyToManyField(Tag)

    # To distinguish if the question is asked by student or created by internal staff
    # we will lookup user's(created_by) type field i.e STUDENT or STAFF
    created_by = models.ForeignKey(
        "users.User", blank=False, null=False, on_delete=models.CASCADE
    )

    def __str__(self):
        return "{} - {}".format(self.title, self.created_by.username)


class UserAskedQuestion(models.Model):
    image = models.ImageField(upload_to=user_asked_question_image_path)
    question = models.ForeignKey(
        Question,
        related_name="user_asked_questions",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return "{}".format(self.question)


class CatalogQuestion(models.Model):
    # these question's will by created_by SMEs i.e internal staff of doubtnut
    question = models.ForeignKey(
        Question,
        related_name="catalog_questions",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
    video_url = models.URLField()
    view_count = models.PositiveIntegerField(blank=True, default=0)

    def __str__(self):
        return "{} -  {} views".format(self.question, self.view_count)


class UserActivity(models.Model):
    catalog_question = models.ForeignKey(
        CatalogQuestion, blank=False, null=False, on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        "users.User", blank=False, null=False, on_delete=models.CASCADE
    )
    last_viewed_at = models.DateTimeField(blank=True, null=True)
    view_count = models.IntegerField(default=0)
    referrer_asked_question = models.ForeignKey(
        UserAskedQuestion, blank=True, null=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return "{} - {}".format(self.user, self.last_viewed_at)
