import os
from celery import Celery
import kombu

from django.conf import settings


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "doubtnut.settings")
app = Celery("tasks", broker="redis://guest@localhost//")

# settings.configure()
app.config_from_object("django.conf:settings")

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


def is_broker_available():
    """
        source: kombu/connection.py

        The connection is established lazily when needed. If you need the
        connection to be established, then force it by calling
        :meth:`connect`::

            >>> conn = Connection('amqp://')
            >>> conn.connect()

        and always remember to close the connection::

            >>> conn.release()

    """
    try:
        conn = kombu.connection.Connection("redis://")
        conn.connect()
        conn.close()
        return True
    except Exception as e:
        print(e)
        print(
            "NOTE: async tasks won't execute unless you start the broker i.e. redis-server"
        )
        return False
