import json

from celery import shared_task
from django_celery_beat.models import CrontabSchedule, PeriodicTask

from decimal import Decimal


@shared_task
def get_price(fuel_id):
    from fuels.models import Fuel

    inst = Fuel.objects.get(pk=fuel_id)
    inst.price = Decimal(
        round(inst.price - (inst.price * inst.coupon.discount) / 100, 2)
    )
    inst.save()
    return inst.price


@shared_task
def get_default_price(fuel_id, discount):
    from fuels.models import Fuel

    inst = Fuel.objects.get(pk=fuel_id)
    inst.price = Decimal(round(inst.price / Decimal(1 - discount / 100), 2))
    inst.save()
    return inst.price


@shared_task
def set_coupon(coupon_id):
    from fuels.models import Coupon, Fuel

    for_set = Coupon.objects.get(id=coupon_id)
    for_set.state = True
    for_set.save()

    Fuel.objects.update(coupon=for_set)


@shared_task
def cancel_coupon(coupon_id):
    from fuels.models import Coupon, Fuel

    for_delete = Coupon.objects.get(id=coupon_id)
    for_delete.state = False
    for_delete.save()
    
    Fuel.objects.filter(coupon__in=for_delete).update(coupon=None)


def coupon_scheduler(coupon_id, date_start, date_end):
    # Set coupon scheduler
    crontab, _ = CrontabSchedule.objects.get_or_create(
        minute=date_start.minute,
        hour=date_start.hour,
        day_of_month=date_start.day,
        month_of_year=date_start.month
    )
    coupon = PeriodicTask.objects.filter(name=f'set-coupon-{coupon_id}')
	
    if not coupon.exists():
        PeriodicTask.objects.create(
            crontab=crontab,
            name=f'set-coupon-{coupon_id}',
            task='users.tasks.set_coupon',
            args=json.dumps([coupon_id]),
		)
    else:
        coupon[0].crontab = crontab
        coupon[0].save()

    # Cancel coupon scheduler
    crontab, _ = CrontabSchedule.objects.get_or_create(
        minute=date_end.minute,
        hour=date_end.hour,
        day_of_month=date_end.day,
        month_of_year=date_end.month
    )

    coupon = PeriodicTask.objects.filter(name=f'cancel-coupon-{coupon_id}')
    if not coupon.exists():
        PeriodicTask.objects.create(
            crontab=crontab,
            name=f'cancel-coupon-{coupon_id}',
            task='users.tasks.cancel_coupon',
            args=json.dumps([coupon_id]),
        )
    else:
        coupon[0].crontab = crontab
        coupon[0].save()
