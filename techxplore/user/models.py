from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q, Sum


class User(AbstractUser):
    personal_number = models.CharField(max_length=11 , unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    avatar = models.ImageField(upload_to='avatars/')
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
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Add this field

    @property
    def months_remaining(self):
        """
        Calculate the number of months remaining to pay off the loan.
        """
        remaining_amount = self.total_due - self.amount_paid
        if self.monthly_payment > 0:
            months = remaining_amount / self.monthly_payment
            return max(0, int(months))
        return 0



    @property
    def total_months(self):
        """
        Calculate the total number of months required to pay off the loan.
        """
        if self.monthly_payment > 0:
            return int(self.total_due / self.monthly_payment)
        return 0

    @property
    def progress(self):
        """
        Calculate the progress of the loan payment as a percentage.
        """
        if self.total_due > 0:
            return (self.amount_paid / self.total_due) * 100
        return 0

    def make_payment(self, amount):
        """
        Record a payment made towards the loan.
        """
        if amount <= 0:
            raise ValueError("Payment amount must be greater than 0.")
        if self.amount_paid + amount > self.total_due:
            raise ValueError("Payment amount exceeds the total due.")
        self.amount_paid += amount
        self.save()

    def __str__(self):
        return f"{self.name} - {self.owner}"


class Utility(models.Model):
    name = models.CharField(max_length=255)
    total_due = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    address = models.CharField(max_length=255)
    subscriber_number = models.CharField(max_length=100)
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