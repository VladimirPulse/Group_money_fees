from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CollectViewSet, PaymentViewSet, UserCreateView

router = DefaultRouter()
router.register(r'collects', CollectViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'users', UserCreateView)

urlpatterns = [
    path('', include(router.urls)),
]
