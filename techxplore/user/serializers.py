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

class UserProfileSerializer(serializers.ModelSerializer):
    loans = serializers.SerializerMethodField()
    utilities = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'personal_number', 'balance', 'loans', 'utilities']

    def get_loans(self, obj):
        return Loan.objects.filter(owner=obj).values('id','name', 'due_date', 'total_due', 'monthly_payment')

    def get_utilities(self, obj):
        return Utility.objects.filter(owner=obj).values('id','name', 'total_due', 'due_date')

class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ["id", "name", "due_date", "total_due", "monthly_payment"]

class UtilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Utility
        fields = ["id", "name", "total_due", "due_date"]

class SenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','personal_number', 'first_name', 'last_name',]

class InvitationSerializer(serializers.ModelSerializer):
    sender = SenderSerializer(read_only=True)
    receiver = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    loan = serializers.PrimaryKeyRelatedField(queryset=Loan.objects.all(), allow_null=True, required=False,
                                              write_only=True)
    utility = serializers.PrimaryKeyRelatedField(queryset=Utility.objects.all(), allow_null=True, required=False,
                                                 write_only=True)

    loan_details = LoanSerializer(source="loan", read_only=True)  # Show full loan details in response
    utility_details = UtilitySerializer(source="utility", read_only=True)

    class Meta:
        model = Invitation
        fields = ["id", "sender", "receiver", "loan","loan_details", "utility_details", "utility", "share_percentage", "status"]


class PaymentAgreementSerializer(serializers.ModelSerializer):

    loan = LoanSerializer(read_only=True)
    utility = UtilitySerializer(read_only=True)

    class Meta:
        model = PaymentAgreement
        fields = ["id","loan", "utility", "share_percentage", "amount_due"]