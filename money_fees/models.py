from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

User = get_user_model()


class Collect(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=255, default="попытка")
    slug = models.CharField(
        max_length=255,
        blank=True,
        choices=[
            ("birthday", "День рождения"),
            ("wedding", "Свадьба"),
        ],
        verbose_name="Повод сбора",
        default="birthday",
    )
    description = models.TextField(verbose_name="Описание")
    sum_fees = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Запланированная сумма сбора",
    )
    curr_sum_fees = models.DecimalField(
        max_digits=10,
        blank=True,
        decimal_places=2,
        default=0,
        verbose_name="Текущая сумма сбора",
    )
    donors_count = models.PositiveIntegerField(blank=True, default=0)
    image = models.ImageField(
        upload_to="images/", blank=True, default=None, null=True
    )
    end_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Группа сбора"
        verbose_name_plural = "Группы сбора"

    def __str__(self):
        return self.title


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    collec_fees = models.ForeignKey(
        Collect, related_name="fees", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Инвестиция"
        verbose_name_plural = "Инвестиции"

    def __str__(self):
        return f"{self.user.username} - {self.amount}"

    def clean(self):
        if self.collec_fees.end_date:
            raise ValidationError(
                f'Выберите другой сбор. Этот сбор завершен {
                    self.collec_fees.end_date.strftime("%Y-%m-%d %H:%M:%S")
                }'
            )
