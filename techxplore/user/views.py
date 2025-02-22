from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status, generics, viewsets, filters
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, UserSerializer, UserProfileSerializer, InvitationSerializer, PaymentAgreementSerializer,ChangeBalanceSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Invitation,PaymentAgreement, Loan, Utility
from django.db import models



User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserInfoView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserViewSet(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["personal_number"]


class InvitationViewSet(viewsets.ModelViewSet):
    serializer_class = InvitationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter invitations to only those sent or received by the authenticated user."""
        user = self.request.user
        return  Invitation.objects.filter(receiver=user)

    def create(self, request, *args, **kwargs):
        """Handle sending multiple invitations for sharing a loan or utility."""
        data = request.data
        sender = request.user


        loan_id = data.get("loan")
        utility_id = data.get("utility")
        receivers_data = data.get("receiver", [])

        if not receivers_data:
            return Response({"error": "At least one receiver is required."}, status=status.HTTP_400_BAD_REQUEST)


        total_percentage = sum([receiver['share_percentage'] for receiver in receivers_data])
        if total_percentage > 100:
            return Response({"error": "Total share percentage cannot exceed 100%."},
                            status=status.HTTP_400_BAD_REQUEST)

        invitations = []
        for receiver_data in receivers_data:
            personal_number = receiver_data["personal_number"]
            share_percentage = receiver_data["share_percentage"]

            receiver = User.objects.filter(personal_number=personal_number).first()
            if not receiver:
                return Response({"error": f"User with personal number {personal_number} not found."},
                                status=status.HTTP_400_BAD_REQUEST)

            invitation = Invitation.objects.create(
                sender=sender,
                loan_id=loan_id,
                utility_id=utility_id,
                share_percentage=share_percentage,
                status="pending"
            )
            invitation.receiver.add(receiver)
            invitations.append(invitation)

        return Response(InvitationSerializer(invitations, many=True).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """Handle invitation acceptance or rejection."""
        invitation = self.get_object()
        status_update = request.data.get("status")

        if status_update not in ["accepted", "declined"]:
            return Response({"error": "Invalid status. Must be 'accepted' or 'declined'."},
                            status=status.HTTP_400_BAD_REQUEST)

        invitation.status = status_update
        invitation.save()

        if status_update == "accepted":

            for receiver in invitation.receiver.all():
                PaymentAgreement.objects.create(
                    user=receiver,
                    loan=invitation.loan,
                    utility=invitation.utility,
                    share_percentage=invitation.share_percentage,
                    amount_due=(
                            (
                                invitation.loan.monthly_payment if invitation.loan else invitation.utility.total_due) * invitation.share_percentage / 100
                    )
                )

            total_accepted_share = sum(
                inv.share_percentage for inv in Invitation.objects.filter(
                    loan=invitation.loan,
                    utility=invitation.utility,
                    status="accepted"
                )
            )


            sender_share = 100 - total_accepted_share


            sender_agreement, created = PaymentAgreement.objects.get_or_create(
                user=invitation.sender,
                loan=invitation.loan,
                utility=invitation.utility,
                defaults={
                    'share_percentage': sender_share,
                    'amount_due': (
                            (
                                invitation.loan.monthly_payment if invitation.loan else invitation.utility.total_due) * sender_share / 100
                    )
                }
            )

            if not created:
                sender_agreement.share_percentage = sender_share
                sender_agreement.amount_due = (
                        (
                            invitation.loan.monthly_payment if invitation.loan else invitation.utility.total_due) * sender_share / 100
                )
                sender_agreement.save()

        return Response(InvitationSerializer(invitation).data)


class PaymentAgreementViewSet(generics.ListAPIView):
    serializer_class = PaymentAgreementSerializer
    permission_classes = [IsAuthenticated]



    def get_queryset(self):
        """
        Get the payment agreements for the authenticated user.
        The user will only see their own payment agreements.
        """
        user = self.request.user

        latest_agreement = PaymentAgreement.objects.filter(user=user).order_by('-id').first()

        return PaymentAgreement.objects.filter(
            id=latest_agreement.id) if latest_agreement else PaymentAgreement.objects.none()


class UpdateUserBalanceView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangeBalanceSerializer

    def put(self, request):
        """
        Update the authenticated user's balance using a PUT request.
        """
        user = request.user  # Get the authenticated user
        serializer = ChangeBalanceSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()  # Update the user's balance
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)