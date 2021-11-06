import stripe

from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponse

from django.shortcuts import render
from django.template import RequestContext
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from products.models import Product

print('stripe: ', settings.STRIPE_SECRET_KEY)
stripe.api_key = settings.STRIPE_SECRET_KEY


class SuccessView(TemplateView):
    template_name = "success.html"


class CancelView(TemplateView):
    template_name = "cancel.html"


class ProductLandingPageView(TemplateView):
    template_name = "landing.html"

    def get_context_data(self, **kwargs):
        product = Product.objects.last()
        context = super(ProductLandingPageView, self).get_context_data(**kwargs)
        context.update({
            "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,
            "product": product,
        })
        return context


class CreateCheckoutSessionView(View):

    def post(self, request, *args, **kwargs):
        YOUR_DOMAIN = "http://127.0.0.1:8000"
        product_id = self.kwargs["pk"]
        product = Product.objects.get(id=product_id)
        print("product: ", product)
        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        # Provide the exact Price ID (e.g. pr_1234) of the product you want to sell
                        "price_data": {
                            "currency": "usd",
                            "unit_amount": product.price,
                            "product_data": {
                                "name": product.name,
                            }
                        },
                        "quantity": 1,
                    },
                ],
                metadata={"product_id": product.id},
                payment_method_types=[
                    "card",
                ],
                mode="payment",
                success_url=YOUR_DOMAIN + '/success/',
                cancel_url=YOUR_DOMAIN + '/cancel/',
            )
            print(f"checkout_session: {checkout_session}")
            return JsonResponse({
                'id': checkout_session.id,
                'url': checkout_session.url,
            })
        except Exception as e:
            print('error: ', e)
            return JsonResponse({
                'error': e,
            })


@csrf_exempt
def stripe_webhook(request):
    print("===========================")
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    print("event: ", event)
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        customer_email = session["customer_details"]["email"]
        product_id = session["metadata"]["product_id"]

        # Fulfill the purchase...
        product = Product.objects.get(id=product_id)
        send_mail(
            subject="Here is your product",
            message=f"Thanks for your purchase. Here is the product you ordered. Url is {product.url}",
            recipient_list=[customer_email],
            from_email="dondrzzy@gmail.com"
        )

    return HttpResponse(status=200)
