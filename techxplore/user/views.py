from django.shortcuts import get_object_or_404
from rest_framework import status, generics, viewsets, filters
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, UserSerializer, UserProfileSerializer, InvitationSerializer, PaymentAgreementSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Invitation,PaymentAgreement


User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data  # Return user details with token
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
    queryset = Invitation.objects.all()
    serializer_class = InvitationSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """Handle sending an invitation to share a loan or utility."""
        sender = request.user
        receiver_personal_number = request.data.get("receiver")
        loan_id = request.data.get("loan")
        utility_id = request.data.get("utility")
        share_percentage = request.data.get("share_percentage")

        # Check if the receiver exists
        receiver = get_object_or_404(User, personal_number=receiver_personal_number)

        # Ensure at least one (Loan or Utility) is provided
        if not loan_id and not utility_id:
            return Response({"error": "You must provide either a Loan or a Utility."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the invitation
        invitation = Invitation.objects.create(
            sender=sender,
            receiver=receiver,
            loan_id=loan_id,
            utility_id=utility_id,
            share_percentage=share_percentage
        )
        return Response(InvitationSerializer(invitation).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """Handle invitation acceptance or rejection."""
        invitation = self.get_object()
        status_update = request.data.get("status")

        if status_update not in ["accepted", "declined"]:
            return Response({"error": "Invalid status. Must be 'accepted' or 'declined'."}, status=status.HTTP_400_BAD_REQUEST)

        invitation.status = status_update
        invitation.save()

        # If accepted, create a payment agreement
        if status_update == "accepted":
            PaymentAgreement.objects.create(
                user=invitation.receiver,
                loan=invitation.loan,
                utility=invitation.utility,
                share_percentage=invitation.share_percentage
            )

        return Response(InvitationSerializer(invitation).data)


class PaymentAgreementViewSet(generics.ListAPIView):
    queryset = PaymentAgreement.objects.all()
    serializer_class = PaymentAgreementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return agreements where the user is involved."""
        return PaymentAgreement.objects.filter(user=self.request.user)