from django.shortcuts import render

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from .models import UserAskedQuestion, Question
from .serializers import (
    QuestionBaseSerializer,
    UserAskedQuestionBaseSerializer,
    UserAskedQuestionDetailSerializer,
)
from .utils import extract_text_from_image, bisect_extracted_question


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
        title, description = bisect_extracted_question(extracted_text)

        question_instance = Question(
            title=title, description=description, created_by=request.user
        )
        question_instance.save()

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
