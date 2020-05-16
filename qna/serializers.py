from rest_framework import serializers

from users.serializers import UserMiniInfoSerializer
from .models import Question, UserAskedQuestion, Tag, CatalogQuestion, UserActivity


class TagBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class QuestionBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = "__all__"


class QuestionDetailSerializer(serializers.ModelSerializer):
    created_by = UserMiniInfoSerializer(read_only=True)
    tags = TagBaseSerializer(read_only=True, many=True)

    class Meta:
        model = Question
        fields = "__all__"


class UserAskedQuestionBaseSerializer(serializers.ModelSerializer):
    user_asked_question_id = serializers.IntegerField(source="id")

    class Meta:
        model = UserAskedQuestion
        fields = "__all__"


class UserAskedQuestionDetailSerializer(serializers.ModelSerializer):
    question = QuestionBaseSerializer(read_only=True)
    user_asked_question_id = serializers.IntegerField(source="id")

    class Meta:
        model = UserAskedQuestion
        fields = "__all__"


class CatalogQuestionBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatalogQuestion
        fields = (
            "question",
            "video_url",
        )


class CatalogQuestionDetailSerializer(serializers.ModelSerializer):
    question = QuestionDetailSerializer(read_only=True)
    catalog_question_id = serializers.IntegerField(source="id")

    class Meta:
        model = CatalogQuestion
        fields = "__all__"


class UserActivityBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivity
        fields = "__all__"
