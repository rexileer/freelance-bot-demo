from core.models import (
    Users,
CustomTexts,
CustomButtons,
Subscription,
SubjectMatters,
Tariffs,
PromoCode,
Bid,
MediaFiles,
ReferralsTable,
UsefulMaterials,
EmptyCheck,
Payments
)
from asgiref.sync import sync_to_async
from django.db.models import F, Q
import datetime
from django.utils import timezone


@sync_to_async
def get_user_by_id(user_id):
    user = Users.objects.filter(id=user_id).first()
    return user


@sync_to_async
def get_or_create_user_by_id(user_id, fio):
    user = Users.objects.filter(id=user_id).first()
    if not user:
        user = Users(id=user_id, fio=fio)
        user.save()
    return user

@sync_to_async
def add_user(user_id, fio):
    user = Users(id=user_id, fio=fio)
    user.save()


@sync_to_async
def get_or_create_custom_text(key, default_text):
    try:
        return CustomTexts.objects.get(key=key).text
    except:
        custom_text = CustomTexts(key=key, text=default_text)
        custom_text.save()
        return default_text


@sync_to_async
def get_or_create_custom_button(key, default_text):
    try:
        button = CustomButtons.objects.get(key=key)
        button.text = default_text
        button.save()
        return button.text
    except:
        custom_button = CustomButtons(key=key, text=default_text)
        custom_button.save()
        return default_text

@sync_to_async
def get_user_subscription_existence(user_id):
    subscriptions = Subscription.objects.filter(user__id=user_id).first()
    return bool(subscriptions)


@sync_to_async
def get_unsubscribed_subject_matters(user_id):
    user_subscriptions = Subscription.objects.filter(user_id=user_id).values_list('matters__id', flat=True)
    unsubscribed_subject_matters = SubjectMatters.objects.exclude(
        id__in=user_subscriptions
    )
    return unsubscribed_subject_matters


@sync_to_async
def get_tariffs():
    return Tariffs.objects.all().order_by('-id')


@sync_to_async
def get_promo_code_by_name(name):
    return PromoCode.objects.filter(name=name).first()


@sync_to_async
def get_selected_subject_matters(matters_ids):
    selected_subject_matters = SubjectMatters.objects.filter(id__in=matters_ids).all()
    return selected_subject_matters


@sync_to_async
def get_tariff_by_id(tariff_id):
    return Tariffs.objects.get(id=tariff_id)


@sync_to_async
def create_subscription(subject_matter_ids, tariff_id, user_id):
    subject_matters = SubjectMatters.objects.filter(id__in=subject_matter_ids)
    tariff = Tariffs.objects.get(id=tariff_id)
    user = Users.objects.get(id=user_id)
    subscription = Subscription.objects.create(
        user=user,
        tariff=tariff,
        end_date=datetime.date.today() + datetime.timedelta(days=tariff.days_open)
    )
    subscription.matters.set(subject_matters)
    subscription.save()
    return subscription


@sync_to_async
def create_free_sub(subject_matter_id, user_id):
    subject_matters = SubjectMatters.objects.filter(id=subject_matter_id)
    user = Users.objects.get(id=user_id)
    subscription = Subscription.objects.create(
        user=user,
        end_date=datetime.date.today() + datetime.timedelta(days=3)
    )
    subscription.matters.set(subject_matters)
    subscription.save()
    user.trial_subscription_expired = True
    user.save()
    return subscription

@sync_to_async
def get_all_subject_matters():
    return SubjectMatters.objects.all()


@sync_to_async
def add_bid(author_username, text, files, matter_ids):
    bid = Bid(author_username=author_username, text=text)
    bid.save()
    for file in files:
        media_file = MediaFiles(path=file["path"], file_type=file["file_type"], tg_file_id=file["tg_file_id"])
        media_file.save()
        bid.files.add(media_file)

    for matter_id in matter_ids:
        matter = SubjectMatters.objects.filter(id=matter_id).first()
        if matter:
            bid.matters.add(matter)
    bid.save()
    return bid


@sync_to_async
def get_count_referrals(referrer):
    count_referrals = ReferralsTable.objects.filter(referrer=referrer).count()
    return count_referrals


@sync_to_async
def add_ref(referrer_id, referred_id):
    ref = ReferralsTable(referrer=Users.objects.get(id=referrer_id), referred=Users.objects.get(id=referred_id))
    ref.save()


@sync_to_async
def top_up_ref_balance(user_id, amount):
    amount = amount / 100 * 10
    referrer = ReferralsTable.objects.filter(referred=Users.objects.get(id=user_id)).first()
    if referrer:
        referrer.referrer.balance += amount
        referrer.referrer.save()
        return True


@sync_to_async
def get_useful_materials():
    return UsefulMaterials.objects.all()


@sync_to_async
def get_useful_material_by_id(material_id):
    return UsefulMaterials.objects.get(id=material_id)


@sync_to_async
def get_search_switch(user_id):
    user = Users.objects.get(id=user_id)
    return user.search_switch


@sync_to_async
def user_search_switch(user_id):
    user = Users.objects.get(id=user_id)
    user.search_switch = False if user.search_switch else True
    user.save()
    return user

@sync_to_async
def get_black_list_by_user(user):
    return user.black_list.all()


@sync_to_async
def get_my_subject_matters(user_id):
    user_subscriptions = Subscription.objects.filter(user_id=user_id)
    matters = []
    for subscriptions in user_subscriptions:
        for matter in subscriptions.matters.all():
            if matter not in matters:
                matters.append(matter)
    return matters


@sync_to_async
def switch_my_category(user_id, subject_matter_id):
    user = Users.objects.get(id=user_id)
    subject_matter = SubjectMatters.objects.get(id=subject_matter_id)

    if subject_matter in user.black_list.all():
        user.black_list.remove(subject_matter)
    else:
        user.black_list.add(subject_matter)
    user.save()


@sync_to_async
def top_up_user_balance(user_id, amount):
    user = Users.objects.get(id=user_id)
    user.balance += amount
    user.save()


@sync_to_async
def take_away_money(user, amount):
    user.balance -= amount
    user.save()


@sync_to_async
def get_mailings():
    incomplete_mailings = Bid.objects.filter(
        Q(is_confirmed=True) & Q(is_sent=False)
        & (Q(mailing_date__lt=timezone.now()) | Q(mailing_date__isnull=True))
    )
    return incomplete_mailings


@sync_to_async
def update_complete_status_bid(bid):
    bid.is_sent = True
    bid.save()


@sync_to_async
def get_users_by_bid_matters(bid):
    users = Users.objects
    if bid.sent_all: return users.all()
    return Subscription.objects.filter(matters__in=bid.matters.all(), end_date__gte=timezone.now()).values_list('user__id', flat=True).distinct()


@sync_to_async
def get_files_by_bid(bid):
    return bid.files.all()


@sync_to_async
def create_empty_check(data, user_id):
    check = EmptyCheck(data=data, user_id=user_id)
    check.save()
    return check


@sync_to_async
def get_check_by_id(check_id):
    check = EmptyCheck.objects.filter(id=check_id).first()
    return check


@sync_to_async
def dell_check(check):
    check.delete()


@sync_to_async
def add_payment(user_id, tariff, previous_invid):
    user = Users.objects.get(id=user_id)
    payments = Payments.objects.create(
        user=user,
        tariff=tariff,
        next_pay_day=datetime.date.today() + datetime.timedelta(days=tariff.days_open),
        previous_invid=previous_invid
    )
    payments.save()
    return payments

