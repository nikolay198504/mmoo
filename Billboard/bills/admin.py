from django.contrib import admin
from .models import Category, Bill, Comment
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms


class BillAdminForm(forms.ModelForm):
    text_bill = forms.CharField(label='Описание', widget=CKEditorUploadingWidget())

    class Meta:
        model = Bill
        fields = '__all__'


class BillAdmin(admin.ModelAdmin):
    form = BillAdminForm

admin.site.register(Bill, BillAdmin)
admin.site.register(Comment)
admin.site.register(Category)
