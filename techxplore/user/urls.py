from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, CustomTokenObtainPairView, UserInfoView, UserViewSet, InvitationViewSet, \
    PaymentAgreementViewSet, UpdateUserBalanceView
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'invitations', InvitationViewSet, basename='invitation')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/profile/', UserInfoView.as_view(), name='user-profile'),
    path('user/finduser/', UserViewSet.as_view(), name='find-user'),
    path('api/invitations/payments/',PaymentAgreementViewSet.as_view(), name='payment-agreements'),
    path('api/changebalance/',UpdateUserBalanceView.as_view(), name='change-balance'),
    path('', include(router.urls)),
]

