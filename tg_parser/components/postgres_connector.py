from core.models import (
    Channels,
SubjectMatters,
Bid
)
from asgiref.sync import sync_to_async
from django.db.models import Q


@sync_to_async
def channel_is_exist(tg_id):
    return Channels.objects.filter(tg_id=tg_id, is_active=True).exists()


@sync_to_async
def get_subject_matters():
    return SubjectMatters.objects.all()


@sync_to_async
def add_bid(matters, author_username, channel_id, text):
    channel = Channels.objects.get(tg_id=channel_id)
    bid = Bid(author_username=author_username, channel=channel, text=text, is_confirmed=True)
    bid.save()
    bid.matters.set(matters)
