from django.conf.urls import url, include


from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

app_name = "users"
urlpatterns = [
    url(r"^api/login/$", obtain_jwt_token),
    url(r"^api/refresh-auth-token/", refresh_jwt_token),
]
