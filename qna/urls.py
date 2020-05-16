from django.conf.urls import url, include
from . import views

from rest_framework import routers

app_name = "qna"

router = routers.SimpleRouter()
router.register(
    r"user-asked-question",
    views.UserAskedQuestionViewSet,
    basename="user_asked_question",
)

urlpatterns = [
    url(r"^api/", include(router.urls)),
]
