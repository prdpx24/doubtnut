from django.conf.urls import url, include
from . import views

from rest_framework import routers

app_name = "qna"

router = routers.SimpleRouter()
router.register(
    r"user-asked-questions",
    views.UserAskedQuestionViewSet,
    basename="user_asked_questions",
)
router.register(
    r"catalog-questions", views.CatalogQuestionViewSet, basename="catalog_questions"
)

urlpatterns = [
    url(r"^api/", include(router.urls)),
]
