from django.contrib import admin
from .models import (Users, CustomTexts, CustomButtons, SubjectMatters, Tariffs,
                     PromoCode, Subscription, Bid, UsefulMaterials, Channels, MediaFiles, ReferralsTable, Payments)
from django.forms import ModelForm
from django.forms.widgets import Textarea, FileInput
from django.forms import ClearableFileInput
from django.db import models
import os
from telethon import TelegramClient
import asyncio
from telethon.tl.functions.channels import JoinChannelRequest
from telethon import utils, types
from django.contrib import messages
from django.utils.safestring import mark_safe
from django import forms

class SubscriptionInline(admin.TabularInline):
    model = Subscription
    extra = 0


class ReferralsInline(admin.TabularInline):
    model = ReferralsTable
    extra = 0
    fk_name = 'referrer'


@admin.register(Users)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "fio")
    exclude = ("black_list",)
    inlines = [SubscriptionInline, ReferralsInline]


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "tariff", "end_date")
    search_fields = ("user",)
    list_filter = ('matters__name',)


@admin.register(MediaFiles)
class MediaFilesAdmin(admin.ModelAdmin):
    list_display = ('get_file_path', 'file_type', 'tg_file_id')
    readonly_fields = ('get_file_path', 'tg_file_id')
    fields = ('path', 'file_type', 'tg_file_id')

    def get_file_path(self, obj):
        if obj.file_type == "photo":
            return mark_safe(f'<img src="/freelance_bot/bot/media/{obj.path}" width="100" height="100" />')
        elif obj.file_type == "video":
            return mark_safe(f'<video src="/freelance_bot/bot/media/{obj.path}" width="100" height="100" controls></video>')
        elif obj.file_type == "document":
            return mark_safe(f'<a href="/freelance_bot/bot/media/{obj.path}">{obj.path}</a>')
        else:
            return "Неизвестный тип файла"

    get_file_path.short_description = "Файл"



class MediaFilesInline(admin.TabularInline):
    model = Bid.files.through
    extra = 0

class SubjectMattersInline(admin.TabularInline):
    model = Bid.matters.through
    extra = 0

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    inlines = [MediaFilesInline, SubjectMattersInline]
    list_display = ('text', 'created_at', 'is_confirmed', "is_sent")
    readonly_fields = ('channel', )
    list_filter = ('is_confirmed',)
    exclude = ("files", "matters")

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        textarea_fields = ['text']
        for field_name in textarea_fields:
            if field_name in form.base_fields:
                form.base_fields[field_name].widget = Textarea(attrs={'rows': 10, 'cols': 80})

        return form


@admin.register(CustomTexts)
class CustomTextsAdmin(admin.ModelAdmin):
    list_display = ('key', 'text')
    search_fields = ('key',)

    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 10, 'cols': 80})},
    }

@admin.register(CustomButtons)
class CustomButtonsAdmin(admin.ModelAdmin):
    list_display = ('key', 'text')
    search_fields = ('key',)

    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 10, 'cols': 80})},
    }


@admin.register(Channels)
class ChannelsAdmin(admin.ModelAdmin):
    list_display = ("id", "channel_link", "is_active")
    readonly_fields = ("tg_id", )

    def save_model(self, request, obj, form, change):
        if not obj.tg_id:
            try:
                obj.tg_id = asyncio.run(self.join_channel(obj.channel_link))
            except Exception as ex:
                messages.error(request, f"Ошибка при сохранении канала: {ex}")
                return
        super().save_model(request, obj, form, change)


    async def join_channel(self, channel_link):
        client = TelegramClient("tg_parser_session", os.getenv("TG_PARSER_API_ID"), os.getenv("TG_PARSER_API_HASH"))
        async with client:
            join_req = await client(JoinChannelRequest(channel_link))
            return join_req.chats[0].id




@admin.register(SubjectMatters)
class SubjectMattersAdmin(admin.ModelAdmin):
    list_display = ("id", "name")

    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 10, 'cols': 80})},
    }


@admin.register(Tariffs)
class TariffsAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "days_open")


@admin.register(PromoCode)
class TariffsAdmin(admin.ModelAdmin):
    list_display = ("name", "discount")


@admin.register(UsefulMaterials)
class UsefulMaterialsAdmin(admin.ModelAdmin):
    list_display = ('title', )
    search_fields = ('title',)

@admin.register(Payments)
class PaymentsAdmin(admin.ModelAdmin):
    pass