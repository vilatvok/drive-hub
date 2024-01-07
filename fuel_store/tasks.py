from celery import shared_task

from django.utils import timezone

from decimal import Decimal


@shared_task
def get_price(fuel_id):
    from fuel_store.models import Fuel

    inst = Fuel.objects.get(pk=fuel_id)
    inst.price = Decimal(
        round(inst.price - (inst.price * inst.coupon.discount) / 100, 2)
    )
    inst.save()
    return inst.price


@shared_task
def get_default_price(fuel_id, discount):
    from fuel_store.models import Fuel

    inst = Fuel.objects.get(pk=fuel_id)
    inst.price = Decimal(round(inst.price / Decimal(1 - discount / 100), 2))
    inst.save()
    return inst.price


@shared_task
def set_coupon():
    from fuel_store.models import Coupon, Fuel

    for_set = Coupon.objects.filter(date_start__gte=timezone.now())
    for_set.update(state=True)

    for_change = Fuel.objects.all()
    for i in for_change:
        i.coupon = for_set.first()
        i.save()


@shared_task
def cancel_coupon():
    from fuel_store.models import Coupon, Fuel

    for_delete = Coupon.objects.filter(date_end__lte=timezone.now())
    for_delete.update(state=False)

    for_change = Fuel.objects.filter(coupon__in=for_delete)
    for i in for_change:
        i.coupon = None
        i.save()

    return "Ok"
