from django.contrib import admin
from .models import User, Loan,Utility, Invitation, PaymentAgreement

# Register your models here.
admin.site.register(User)
admin.site.register(Loan)
admin.site.register(Utility)
admin.site.register(Invitation)
admin.site.register(PaymentAgreement)