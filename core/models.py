from email.policy import default

from django.db import models
import datetime
from django.db.models import F

class Users(models.Model):
    id = models.BigIntegerField(primary_key=True)
    fio = models.CharField(max_length=255, blank=True, null=True, verbose_name="ФИО пользователя")
    balance = models.BigIntegerField(null=True, default=0, verbose_name="Баланс")
    search_switch = models.BooleanField(default=True, verbose_name="Включен ли поиск")
    black_list = models.ManyToManyField("SubjectMatters", verbose_name="Черный список")
    trial_subscription_expired = models.BooleanField(default=False, verbose_name="Пробная подписка потрачена")


    class Meta:
        db_table = 'users'
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return str(self.fio)


class SubjectMatters(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(blank=True, verbose_name="Название")
    keywords = models.CharField(blank=True, verbose_name="Ключевые слова")

    class Meta:
        db_table = 'subject_matters'
        verbose_name = "Тематика"
        verbose_name_plural = "Тематики"

    def __str__(self):
        return self.name



class Tariffs(models.Model):
    id = models.BigAutoField(primary_key=True)
    price = models.BigIntegerField(blank=True, verbose_name="Цена")
    days_open = models.BigIntegerField(blank=True, verbose_name="Кол-во дней доступа")
    title = models.CharField(blank=True, verbose_name="Название")

    class Meta:
        db_table = 'tariffs'
        verbose_name = "Тариф"
        verbose_name_plural = "Тарифы"

    def __str__(self):
        return self.title


class PromoCode(models.Model):
    name = models.CharField(blank=True, verbose_name="Промокод")
    discount = models.BigIntegerField(verbose_name="Скидка в процентах")

    class Meta:
        db_table = 'promo_code'
        verbose_name = "Промокод"
        verbose_name_plural = "Промокоды"

    def __str__(self):
        return self.name


class MediaFiles(models.Model):
    path = models.FileField(blank=True, verbose_name="Путь")
    file_type = models.CharField(blank=True, verbose_name="Тип файла")
    tg_file_id = models.CharField(null=True, verbose_name="Tg id")

    class Meta:
        db_table = 'media_files'
        verbose_name = "Файл"
        verbose_name_plural = "Файлы"

    def __str__(self):
        return str(self.path)


class Subscription(models.Model):
    matters = models.ManyToManyField(SubjectMatters, verbose_name="Тематики")
    user = models.ForeignKey(Users, on_delete=models.CASCADE, verbose_name="Пользователь")
    tariff = models.ForeignKey(Tariffs, null=True, on_delete=models.CASCADE, verbose_name="Тариф")
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    end_date = models.DateField(verbose_name="Дата окончания подписки")

    class Meta:
        db_table = 'subscription'
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return str(self.id)


class CustomTexts(models.Model):
    key = models.CharField(verbose_name="Ключ")
    text = models.CharField(blank=True, verbose_name="Текст")

    class Meta:
        db_table = 'custom_texts'
        verbose_name = "Текст"
        verbose_name_plural = "Текста в боте"

    def __str__(self):
        return self.text


class CustomButtons(models.Model):
    key = models.CharField(verbose_name="Ключ")
    text = models.CharField(blank=True, verbose_name="Текст")

    class Meta:
        db_table = 'custom_buttons'
        verbose_name = "Кнопка"
        verbose_name_plural = "Кнопки"

    def __str__(self):
        return self.text


class Channels(models.Model):
    channel_link = models.CharField(max_length=255, blank=True, verbose_name="Адрес канала")
    tg_id = models.BigIntegerField(blank=True, null=True, verbose_name="TG id канала")
    is_active = models.BooleanField(default=True, blank=True, verbose_name="Канал включен")

    class Meta:
        db_table = 'channels'
        verbose_name = "Telegram канал"
        verbose_name_plural = "Telegram каналы"

    def __str__(self):
        return self.channel_link


class Bid(models.Model):
    matters = models.ManyToManyField(SubjectMatters, verbose_name="Тематики")
    sent_all = models.BooleanField(default=False, verbose_name="Отправить всем")
    author_username = models.CharField(null=True, blank=True, verbose_name="Автор")
    channel = models.ForeignKey(Channels, on_delete=models.CASCADE, default=None, null=True, verbose_name="Канал")
    text = models.CharField(blank=True, null=True, verbose_name="Текст")
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    files = models.ManyToManyField(MediaFiles, verbose_name="Файлы")
    is_confirmed = models.BooleanField(default=False, verbose_name="Подтверждена")
    is_sent = models.BooleanField(default=False, verbose_name="Отправлена")
    mailing_date = models.DateTimeField(default=None, blank=True, null=True, verbose_name="Дата отправки")

    class Meta:
        db_table = 'bid'
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"

    def __str__(self):
        return repr(self.text)


class ReferralsTable(models.Model):
    referrer = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='referrals', verbose_name="Реферер")
    referred = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='referred_by', verbose_name="Реферал")

    class Meta:
        db_table = 'referrals'
        verbose_name = "Реферал"
        verbose_name_plural = "Рефералы"


class EmptyCheck(models.Model):
    data = models.CharField(blank=True)
    user_id = models.BigIntegerField()

    class Meta:
        db_table = 'empty_check'


class UsefulMaterials(models.Model):
    url = models.CharField(blank=True, verbose_name="Ссылка")
    text = models.CharField(blank=True, verbose_name="Текст")
    title = models.CharField(blank=True, verbose_name="Заголовок")
    image = models.ImageField(blank=True, verbose_name="Картинка")
    video = models.FileField(blank=True, verbose_name="Видео")

    class Meta:
        db_table = 'useful_materials'
        verbose_name = "Материал"
        verbose_name_plural = "Полезные материалы"

    def __str__(self):
        return self.text


class Payments(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, verbose_name="Пользователь")
    tariff = models.ForeignKey(Tariffs, null=True, on_delete=models.CASCADE, verbose_name="Тариф")
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    next_pay_day = models.DateField(verbose_name="Следующий платеж")
    previous_invid = models.BigIntegerField(verbose_name="Предыдущий invid")

    class Meta:
        db_table = 'payments'
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"

    def __str__(self):
        return str(self.id)
