from django.contrib import admin
from django.urls import path

from products.views import (
    CreateCheckoutSessionView,
    ProductLandingPageView,
    SuccessView,
    CancelView,
    stripe_webhook,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("webhooks/stripe/", stripe_webhook, name="stripe_webhook"),
    path("success/", SuccessView.as_view(), name="success"),
    path("cancel/", CancelView.as_view(), name="cancel"),
    path("", ProductLandingPageView.as_view(), name="landing_page"),
    path("create-checkout-session/<pk>/", CreateCheckoutSessionView.as_view(), name="create_checkout_session")
]
