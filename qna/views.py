from django.shortcuts import render

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from .models import UserAskedQuestion, Question, Tag
from .serializers import (
    QuestionBaseSerializer,
    UserAskedQuestionBaseSerializer,
    UserAskedQuestionDetailSerializer,
)
from .utils import (
    extract_text_from_image,
    bisect_extracted_question,
    get_possible_tags_from_text,
)


class UserAskedQuestionViewSet(viewsets.ModelViewSet):
    queryset = UserAskedQuestion.objects.none()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserAskedQuestionBaseSerializer

    def create(self, request, *args, **kwargs):
        # in-memory image file
        uploaded_image = request.data.get("image")
        extracted_text = extract_text_from_image(uploaded_image)

        if extracted_text is None:
            extracted_text = "Generic Question Title\nGeneric Description"

        # create question instance
        possible_tags = get_possible_tags_from_text(extracted_text)

        title, description = bisect_extracted_question(extracted_text)

        question_instance = Question(
            title=title, description=description, created_by=request.user
        )
        question_instance.save()
        for tag_key in possible_tags:
            tag_instance, created = Tag.objects.get_or_create(name=tag_key)
            question_instance.tags.add(tag_instance)

        # set pointer back to start of file
        uploaded_image.seek(0)
        data = {"image": uploaded_image, "question": question_instance.id}
        serializer = UserAskedQuestionBaseSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user_asked_question_instance = serializer.save()

        resp_serializer = UserAskedQuestionDetailSerializer(
            user_asked_question_instance
        )
        return Response(resp_serializer.data, status=status.HTTP_201_CREATED)
