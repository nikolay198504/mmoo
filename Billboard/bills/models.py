from django.db import models
from ckeditor.fields import RichTextField
from django.contrib.auth.models import AbstractUser
from django.urls import reverse



class User(AbstractUser):
    code = models.CharField(max_length=15, blank=True, null=True)


class Category(models.Model):
    name = models.CharField(max_length=25, unique=True, verbose_name='Категории')

    def __str__(self):
        return self.name


class Bill(models.Model):

    tanks = 'TK'
    hils = 'HL'
    dd = 'DD'
    merchants = 'MH'
    guild_masters = 'GM'
    quest_givers = 'QM'
    blacksmiths = 'BS'
    tanners = 'TN'
    potion_makers = 'PM'
    spell_masters = 'SM'

    BILL_TYPES = [
        (tanks, 'Танки'),
        (hils, 'Хилы'),
        (dd, 'ДД'),
        (merchants, 'Торговцы'),
        (guild_masters, 'Гилдмастеры'),
        (quest_givers, 'Квестгиверы'),
        (blacksmiths, 'Кузнецы'),
        (tanners, 'Кожевники'),
        (potion_makers, 'Зельевары'),
        (spell_masters, 'Мастера заклинаний'),
    ]

    bill_time = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    text = RichTextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")
    category = models.ManyToManyField(Category, through='BillCategory', verbose_name="Категория")

    def __str__(self):
        return f'id-{self.pk}: {self.title}'

    def get_absolute_url(self):
        return reverse('bill_detail', args=[str(self.pk)])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class BillCategory(models.Model):
    bill = models.ForeignKey('Bill', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text_comment = models.TextField(max_length=255)
    comment_bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    date_in = models.DateTimeField(auto_now_add=True)
    comment = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('mycomments', args=[str(self.comment_bill.id)])


class OneTimeCode(models.Model):
    user = models.CharField(max_length=256)
    code = models.CharField(max_length=10)
