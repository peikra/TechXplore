from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Loan, Utility, Invitation, PaymentAgreement

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username', 'personal_number', 'first_name', 'last_name', 'balance']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['personal_number','username', 'first_name', 'last_name', 'password','balance']

    def create(self, validated_data):
        user = User.objects.create_user(
            personal_number=validated_data['personal_number'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password'],
            username=validated_data['username'],
            balance=validated_data['balance']
        )
        return user

class LoanSerializer(serializers.ModelSerializer):
    months_remaining = serializers.SerializerMethodField()
    total_months = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Loan
        fields = [
            "id",
            "name",
            "due_date",
            "total_due",
            "monthly_payment",
            "amount_paid",
            "months_remaining",
            "total_months",
            "progress",
        ]

    def get_months_remaining(self, obj):
        """Serialize the months_remaining property."""
        return obj.months_remaining

    def get_total_months(self, obj):
        """Serialize the total_months property."""
        return obj.total_months

    def get_progress(self, obj):
        """Serialize the progress property."""
        return obj.progress


class UserProfileSerializer(serializers.ModelSerializer):
    loans = serializers.SerializerMethodField()
    utilities = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'personal_number', 'balance', 'loans', 'utilities']

    def get_loans(self, obj):
        loans = Loan.objects.filter(owner=obj)
        return LoanSerializer(loans, many=True).data

    def get_utilities(self, obj):
        utilities = Utility.objects.filter(owner=obj)
        return utilities.values('id', 'name', 'total_due', 'due_date', 'address', 'subscriber_number')

class UtilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Utility
        fields = ["id", "name", "total_due", "due_date","address","subscriber_number"]

class SenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','personal_number', 'first_name', 'last_name',]

class InvitationSerializer(serializers.ModelSerializer):
    sender = SenderSerializer(read_only=True)
    loan = serializers.PrimaryKeyRelatedField(queryset=Loan.objects.all(), allow_null=True, required=False, write_only=True)
    utility = serializers.PrimaryKeyRelatedField(queryset=Utility.objects.all(), allow_null=True, required=False, write_only=True)
    loan_details = serializers.SerializerMethodField()
    utility_details = serializers.SerializerMethodField()

    class Meta:
        model = Invitation
        fields = ["id", "sender", "loan", "loan_details", "utility_details", "utility", "share_percentage", "status"]

    def get_loan_details(self, obj):
        if obj.loan:
            return {"name": obj.loan.name, "monthly_payment": obj.loan.monthly_payment}
        return None

    def get_utility_details(self, obj):
        if obj.utility:
            return {"name": obj.utility.name, "total_due": obj.utility.total_due}
        return None


class PaymentAgreementSerializer(serializers.ModelSerializer):
    loan = LoanSerializer(read_only=True)
    utility = UtilitySerializer(read_only=True)

    class Meta:
        model = PaymentAgreement
        fields = ["id","loan", "utility", "share_percentage", "amount_due"]

class ChangeBalanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['balance']