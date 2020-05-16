from users.models import User
from users.serializers import UserDetailSerializer


def custom_jwt_response_payload_handler(token, user=None, request=None):
    return {
        "token": token,
        "user": UserDetailSerializer(user, context={"request": request}).data,
    }
