from django.contrib import admin
from django.utils.html import format_html
from .models import User, Loan, Utility, Invitation, PaymentAgreement


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "personal_number", "balance", "username")
    search_fields = ("first_name", "last_name", "personal_number", "username")
    list_filter = ("balance",)


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "total_due", "amount_paid",  "due_date")
    list_filter = ("due_date",)
    search_fields = ("name", "owner__first_name", "owner__last_name")


@admin.register(Utility)
class UtilityAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "total_due", "due_date", "address", "subscriber_number")
    list_filter = ("due_date",)
    search_fields = ("name", "owner__first_name", "owner__last_name", "subscriber_number")


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ("sender", "receivers_display", "share_percentage", "status")
    list_filter = ("status",)
    search_fields = ("sender__first_name", "sender__last_name")

    def receivers_display(self, obj):
        return ", ".join([str(receiver) for receiver in obj.receiver.all()])

    receivers_display.short_description = "Receivers"


@admin.register(PaymentAgreement)
class PaymentAgreementAdmin(admin.ModelAdmin):
    list_display = ("user", "share_percentage", "amount_due", "loan", "utility")
    list_filter = ("loan", "utility")
    search_fields = ("user__first_name", "user__last_name")


admin.site.site_header = "Finance Manager Admin"
admin.site.site_title = "Finance Manager"
admin.site.index_title = "Manage Loans, Utilities, and Payments"
