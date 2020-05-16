from rest_framework import serializers

from .models import Question, UserAskedQuestion


class QuestionBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = "__all__"


class UserAskedQuestionBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAskedQuestion
        fields = "__all__"


class UserAskedQuestionDetailSerializer(serializers.ModelSerializer):
    question = QuestionBaseSerializer(read_only=True)

    class Meta:
        model = UserAskedQuestion
        fields = "__all__"
