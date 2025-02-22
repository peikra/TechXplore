from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q, Sum


class User(AbstractUser):
    personal_number = models.CharField(max_length=11 , unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50,unique=True)
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.personal_number})"


class Loan(models.Model):
    name = models.CharField(max_length=255)
    total_due = models.DecimalField(max_digits=10, decimal_places=2)
    monthly_payment = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="loans")

    def __str__(self):
        return f"{self.name} - {self.owner}"


class Utility(models.Model):
    name = models.CharField(max_length=255)
    total_due = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="utilities")

    def __str__(self):
        return f"{self.name} - {self.owner}"


class Invitation(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_invitations")
    receiver = models.ManyToManyField(User, related_name="received_invitations")
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, null=True, blank=True)
    utility = models.ForeignKey(Utility, on_delete=models.CASCADE, null=True, blank=True)
    share_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=20, choices=[("pending", "Pending"), ("accepted", "Accepted"), ("declined", "Declined")], default="pending")



    def __str__(self):
        receivers = ", ".join([str(receiver) for receiver in self.receiver.all()])
        return f"{self.sender} invited {receivers} to share {self.share_percentage}% of {self.loan or self.utility}"

class PaymentAgreement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="agreements")
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, null=True, blank=True)
    utility = models.ForeignKey(Utility, on_delete=models.CASCADE, null=True, blank=True)
    share_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)


    def __str__(self):
        return f"{self.user} pays {self.share_percentage}% of {self.loan or self.utility}"