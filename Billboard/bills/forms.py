from django import forms
from .models import Bill, Comment
from ckeditor.fields import RichTextFormField
from allauth.account.forms import SignupForm
from string import hexdigits
import random
from django.conf import settings
from django.core.mail import send_mail


class BillForm(forms.ModelForm):

    class Meta:
        model = Bill
        fields = ['category', 'title', 'text']
        widgets = {
            'text': RichTextFormField(),
        }


    def __init__(self, *args, **kwargs):
        super(BillForm, self).__init__(*args, **kwargs)
        self.fields['category'].label = "Категория:"
        self.fields['title'].label = "Заголовок:"
        self.fields['text'].label = "Текст объявления:"



class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text_comment']

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['text_comment'].label = "Текст отклика:"

class CommonSignupForm(SignupForm):
    def save(self, request):
        user = super(CommonSignupForm, self).save(request)
        user.is_active = False
        code = '' .join(random.sample(hexdigits, 5))
        user.code = code
        user.save()
        send_mail(
            subject=f'Код активации',
            message=f'Код активации аккаунта: {code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )
        return user
