from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Comment, Bill
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string


@receiver(post_save, sender=Bill)
def create_bill(sender, instance, created, **kwargs):
    if created:
        print(f'{instance.title} {instance.created.strftime("%Y-%M-%d")}')


@receiver(post_save, sender=Comment)
def send_message_comment(sender, instance, created, **kwargs):
    if created:
        print(f'''Пользователь {instance.user.email}, откликнулся на ваше объявление - '{instance.comment_bill.title}' ''')

        html_content = render_to_string('comment_created_email.html', {'instance': instance, })

        msg = EmailMultiAlternatives(
            subject=f'Отклик на объявление - {instance.text}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[instance.comment_bill.author.email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
