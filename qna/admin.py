from django.contrib import admin

from .models import Question, UserAskedQuestion, CatalogQuestion, UserActivity, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
    )
    search_fields = ("name",)


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


@admin.register(CatalogQuestion)
class CatalogQuestionAdmin(admin.ModelAdmin):
    list_display = ("question",)
    list_filter = ("question__tags",)
    search_fields = ["question__title", "video_url"]


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = (
        "catalog_question",
        "last_viewed_at",
        "user",
    )
    list_filter = ("catalog_question__question__tags",)
    search_fields = ["catalog_question__question__title", "catalog_question__video_url"]
