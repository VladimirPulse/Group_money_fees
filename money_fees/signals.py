import datetime as dt

from django.db.models.signals import post_save
from django.dispatch import receiver

from money_fees.models import Payment


@receiver(post_save, sender=Payment)
def update_collect_on_payment(sender, instance, created, **kwargs):
    # import pdb;pdb.set_trace()
    if created:
        collec = instance.collec_fees
        # Обновляем сумму
        collec.curr_sum_fees += instance.amount
        # Обновляем число доноров
        if (
            not Payment.objects.filter(user=instance.user, collec_fees=collec)
            .exclude(id=instance.id)
            .exists()
        ):
            collec.donors_count += 1
        # Проверка завершения
        if collec.sum_fees <= collec.curr_sum_fees:
            collec.end_date = dt.datetime.now()
        collec.save()
