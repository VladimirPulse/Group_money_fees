from django.contrib import admin

from money_fees.models import Collect, Payment


@admin.register(Collect)
class CollectAdmin(admin.ModelAdmin):
    list_display = (
        "author",
        "title",
        "slug",
        "description",
        "sum_fees",
        "curr_sum_fees",
        "donors_count",
        "end_date",
    )
    list_filter = ("author", "slug", "end_date")
    search_fields = ("author", "title", "slug", "end_date")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "created_at", "collec_fees")
    list_filter = ("user", "created_at", "collec_fees")
    search_fields = ("user", "created_at", "collec_fees")
