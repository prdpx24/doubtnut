import os

from django.utils import timezone
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.files import File

from tasks import app, is_broker_available

from users.models import UserNotificationHistory
from qna.models import UserActivity, CatalogQuestion
from qna.queries import (
    get_previous_viewed_catalog_question_ids,
    query_similar_catalog_question_by_asked_question,
)
from qna.utils import generate_pdf_document_from_catalog_questions


def trigger_async_task_on_user_inactivity(user, user_asked_question):
    previously_viewed_catalog_question_ids = get_previous_viewed_catalog_question_ids(
        user
    )
    related_catalog_questions = query_similar_catalog_question_by_asked_question(
        user_asked_question,
        exclude_catalog_question_ids=previously_viewed_catalog_question_ids,
    )[:10]

    # generate pdf file right now, spare celery from doing Disk IO
    pdf_filepath = generate_pdf_document_from_catalog_questions(
        related_catalog_questions
    )
    # and create entry in UserNotificationHistory
    notification_log = UserNotificationHistory.objects.create(user=user)
    # save generated pdf in media assets(S3 or local)
    notification_log.email_attachment.save(
        "catalog_questions_via_asked_question_{}_.pdf".format(user_asked_question.id),
        File(open(pdf_filepath, "rb")),
    )
    # delete /tmp/ generated_catalog.pdf
    try:
        os.remove(pdf_filepath)
    except Exception as e:
        print(e)

    if is_broker_available():
        execute_async_user_inactivity_email.apply_async(
            (user, related_catalog_questions, user_asked_question, notification_log),
            eta=timezone.now()
            + timezone.timedelta(minutes=settings.INACITIVITY_EMAIL_TIME),
        )


@app.task(bind=True)
def execute_async_user_inactivity_email(
    self, user, catalog_questions, user_asked_question, notification_log
):
    last_5_minutes = timezone.now() - timezone.timedelta(
        minutes=settings.INACITIVITY_EMAIL_TIME
    )
    did_we_sent_any_email_in_last_5_minutes_to_user = UserNotificationHistory.objects.filter(
        triggered_at__gte=last_5_minutes, user=user
    ).exists()
    if did_we_sent_any_email_in_last_5_minutes_to_user:
        print("we already sent him an email")
        # delete useless notification log
        notification_log.delete()
        # and do nothing
        return

    did_user_viewed_any_other_video_in_last_5_minutes = UserActivity.objects.filter(
        user=user,
        referrer_asked_question=user_asked_question,
        last_viewed_at__gte=last_5_minutes,
    ).exists()
    if did_user_viewed_any_other_video_in_last_5_minutes:
        notification_log.delete()
        # and do nothing
        return

    subject = "You might want to try these questions | Doubtnut"

    text_body = """Hi {user_first_name},
Thanks for submitting the question. 
Our team is already working on it to provide the best possible solution.
Meanwhile, you should checkout our recommended set of questions(with video explaination) similar to the question you just asked.

Download: {link} 

Regards,
Team Doubtnut
""".format(
        user_first_name=user.first_name, link=notification_log.email_attachment.url
    )

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.NOTIFICATION_EMAIL,
        to=[user.email],
    )
    # mailgun is not configured, so let it fail silently
    msg.send(fail_silently=True)
    print("subject", subject)
    notification_log.email_subject = subject
    notification_log.triggered_at = timezone.now()
    notification_log.save()
    print("notification_log", notification_log)
