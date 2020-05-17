from django.utils import timezone
from rest_framework import viewsets, permissions, status, decorators
from rest_framework.response import Response


from users.constants import UserType
from .models import UserAskedQuestion, Question, Tag, CatalogQuestion, UserActivity
from .serializers import (
    QuestionBaseSerializer,
    UserAskedQuestionBaseSerializer,
    UserAskedQuestionDetailSerializer,
    CatalogQuestionBaseSerializer,
    UserActivityBaseSerializer,
    CatalogQuestionDetailSerializer,
)
from .queries import (
    get_previous_viewed_catalog_question_ids,
    query_similar_catalog_question_by_asked_question,
)
from .utils import (
    extract_text_from_image,
    bisect_extracted_question,
    get_possible_tags_from_text,
)
from .tasks import trigger_async_task_on_user_inactivity


class UserAskedQuestionViewSet(viewsets.ModelViewSet):
    queryset = UserAskedQuestion.objects.none()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserAskedQuestionBaseSerializer

    def create(self, request, *args, **kwargs):
        """
        url: /qna/api/user-asked-questions/
        method: POST
        data: {"image":<image>}
        """
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


class CatalogQuestionViewSet(viewsets.ModelViewSet):
    queryset = CatalogQuestion.objects.select_related("question")
    serializer_class = CatalogQuestionBaseSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def list(self, request):
        """
        method: GET
        url: /qna/api/catalog-questions/?asked_question_id=<user_asked_question_pk>
        """
        asked_question_id = request.query_params.get("asked_question_id")
        if not asked_question_id:
            return Response(
                {"msg": "asked_question_id is required param"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        asked_question = UserAskedQuestion.objects.filter(id=asked_question_id).first()
        if not asked_question:
            return Response(
                {"msg": "Invalid asked_question_id"}, status=status.HTTP_400_BAD_REQUEST
            )

        # we need to exclude previously viewed catalog question by user in last 2 days
        previous_viewed_catalog_question_ids = get_previous_viewed_catalog_question_ids(
            request.user
        )

        # and then order the result by view_count from highest to lowest
        catalog_questions = query_similar_catalog_question_by_asked_question(
            asked_question,
            exclude_catalog_question_ids=previous_viewed_catalog_question_ids,
        )
        serializer = CatalogQuestionDetailSerializer(catalog_questions[:10], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        """
        url: /qna/api/catalog-questions/
        method: POST
        data:
        {
            "question":{
                "title":"...",
                "description":"...",
                "tags":[1,2,3]
            },
            "video_url":"https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        }
        """
        if request.user.type == UserType.STUDENT:
            return Response({"msg": "Prohibited"}, status=status.HTTP_403_FORBIDDEN)

        if type(request.data.get("question")) in (str, int):
            question_instance = Question.objects.filter(
                id=request.data.get("question")
            ).first()
        else:
            question_data = request.data.get("question")
            question_data["created_by"] = request.user.id
            question_serializer = QuestionBaseSerializer(data=question_data)
            question_serializer.is_valid(raise_exception=True)
            question_instance = question_serializer.save()

        catalog_question_data = {
            "question": question_instance.id,
            "video_url": request.data.get("video_url"),
        }
        catalog_question_serializer = CatalogQuestionBaseSerializer(
            data=catalog_question_data
        )
        catalog_question_serializer.is_valid(raise_exception=True)
        catalog_question_instance = catalog_question_serializer.save()

        serializer = CatalogQuestionDetailSerializer(catalog_question_instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @decorators.action(
        methods=["put",],
        detail=True,
        permission_classes=[permissions.IsAuthenticated,],
    )
    def watch_video(self, request, pk=None):
        # NOTE
        # GET request would have made sense if we have just returned result without modifying table,
        # since, we have to modify the view_count of catalog question & update user_activity, we will go with PUT request
        """
        url: /qna/api/catalog-questions/<catalog_question_pk>/watch_video/
        method:PUT
        data:
        {
            "asked_question_id":<asked_question_pk>,
            "trigger_email_on_inactivity":false
        }
        """
        catalog_question = self.get_object()
        catalog_question.view_count += 1
        catalog_question.save()
        asked_question_id = request.data.get("asked_question_id")
        if asked_question_id:
            asked_question = UserAskedQuestion.objects.filter(
                id=asked_question_id
            ).first()
        else:
            asked_question = None
        if asked_question is None:
            return Response(
                {"msg": "Invalid asked_question_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user_activity, created = UserActivity.objects.get_or_create(
            catalog_question=catalog_question,
            user=request.user,
            referrer_asked_question=asked_question,
        )
        user_activity.last_viewed_at = timezone.now()
        user_activity.view_count += 1
        user_activity.save()

        currently_viewed_catalog_question_data = CatalogQuestionDetailSerializer(
            catalog_question
        ).data

        # we need to exclude previously viewed catalog question by user in last 2 days
        previous_viewed_catalog_question_ids = get_previous_viewed_catalog_question_ids(
            request.user
        )

        # and then order the result by view_count from highest to lowest
        related_catalog_qs = query_similar_catalog_question_by_asked_question(
            asked_question,
            exclude_catalog_question_ids=previous_viewed_catalog_question_ids,
        )

        related_catalog_questions = CatalogQuestionDetailSerializer(
            related_catalog_qs[:10], many=True
        ).data

        currently_viewed_catalog_question_data[
            "related_questions"
        ] = related_catalog_questions

        trigger_email_on_inactivity = request.data.get("trigger_email_on_inactivity")
        if trigger_email_on_inactivity:
            # trigger async celery task
            trigger_async_task_on_user_inactivity(request.user, asked_question)

        return Response(
            currently_viewed_catalog_question_data, status=status.HTTP_200_OK
        )

    @decorators.action(
        methods=["POST",],
        detail=False,
        permission_classes=[permissions.IsAuthenticated,],
    )
    def send_mail_on_user_inactivity(self, request):
        """
        {
            "current_catalog_question_id":<catalog_question_id>,
            "asked_question_id":<asked_question_id>,
        }
        """
        # TODO
        try:
            asked_question_id = request.data.get("asked_question_id")
            user_asked_question = UserAskedQuestion.objects.get(id=asked_question_id)
            trigger_async_task_on_user_inactivity(request.user, user_asked_question)
            return Response(
                {"msg": "Catalog question set is queued for user"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            print("** exception in executing async task**")
            print(e)
        return Response(
            {"msg": "Failed to execute async task"}, status=status.HTTP_200_OK,
        )
