from django.utils import timezone

from users.models import User
from .models import UserActivity, CatalogQuestion


def get_previous_viewed_catalog_question_ids(user):
    last_2_days = timezone.now() - timezone.timedelta(days=3)
    previously_viewed_question_ids = UserActivity.objects.filter(
        user=user, last_viewed_at__gte=last_2_days
    ).values_list("catalog_question_id", flat=True)
    return previously_viewed_question_ids


def query_similar_catalog_question_by_asked_question(
    asked_question, exclude_catalog_question_ids=[]
):
    tags = asked_question.question.tags.all()
    qs = CatalogQuestion.objects.filter(question__tags__in=tags).select_related(
        "question"
    )
    if exclude_catalog_question_ids:
        qs = qs.exclude(id__in=exclude_catalog_question_ids)
    return qs.order_by("-view_count")
