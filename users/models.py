from django.db import models
from django.contrib.auth.models import AbstractUser

from .constants import UserType


class User(AbstractUser):
    """
    Schema for users table
    first_name, last_name, email, username & password are 
    already declared in BaseClass `AbstractUser` 
    """

    TYPE_CHOICES = ((UserType.STAFF, "Staff"), (UserType.STUDENT, "Student"))

    type = models.CharField(
        choices=TYPE_CHOICES,
        max_length=10,
        blank=False,
        null=False,
        default=UserType.STUDENT,
    )

    GENDER_CHOICES = (("M", "Male"), ("F", "Female"), ("O", "Other"))
    gender = models.CharField(
        choices=GENDER_CHOICES, max_length=2, blank=True, null=True
    )

    @property
    def full_name(self):
        if self.first_name:
            return self.first_name + " " + self.last_name if self.last_name else ""
        else:
            # fallback to username if first_name is null
            return self.username

    def __str__(self):
        return "{} - {}".format(self.full_name, self.email)
