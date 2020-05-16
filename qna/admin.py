from django.contrib import admin

from .models import Question, UserAskedQuestion


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("title", "created_by")
    list_filter = ("tags",)
    search_fields = ["title", "description", "created_by__email"]


@admin.register(UserAskedQuestion)
class UserAskedQuestionAdmin(admin.ModelAdmin):
    list_display = ("question",)
    list_filter = ("question__tags",)
    search_fields = ["question__title", "question__created_by__email"]
