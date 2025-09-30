import requests
import uuid
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from apps.products.models import Order, OrderItem, CartItem, Cart, ProductVariant
from .models import PaymentTransaction

class PaymentAndOrderCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Get user's cart
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart_items = CartItem.objects.filter(cart=cart)
            
            if not cart_items.exists():
                return Response(
                    {"error": "Cart is empty"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Calculate total amount using cart's method
            total_amount = cart.total_price()

            # Create order
            order = Order.objects.create(
                user=request.user,
                status='pending',
                delivery_method=request.data.get('delivery_method', 'pickup'),
                customer_name=f"{request.user.first_name} {request.user.last_name}",
                customer_email=request.user.email,
                customer_phone=request.data.get('customer_phone', ''),
                address=request.data.get('address', ''),
                city=request.data.get('city', ''),
                state=request.data.get('state', ''),
                zip_code=request.data.get('zip_code', ''),
                pickup_date=request.data.get('pickup_date', None),
                total_amount=total_amount,
                is_paid=False
            )

            # Create order items from cart items (but don't reduce stock yet)
            for cart_item in cart_items:
                if cart_item.product:
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        size=cart_item.size,
                        price=cart_item.product.price
                    )
                elif cart_item.headwear_product:
                    OrderItem.objects.create(
                        order=order,
                        headwear_product=cart_item.headwear_product,
                        quantity=cart_item.quantity,
                        price=cart_item.headwear_product.price
                    )

            # Prepare response with order details for payment
            response_data = {
                "order_id": order.id,
                "order_number": order.order_number,
                "amount": str(total_amount),
                "email": order.customer_email,
                "first_name": request.user.first_name or "",
                "last_name": request.user.last_name or "",
                "status": "order_created",
                "message": "Order created successfully. Proceeding to payment."
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )




# In payments/views.py - Update PaymentInitiateView
class PaymentInitiateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            order_id = request.data.get('order_id')
            if not order_id:
                return Response(
                    {"error": "Order ID is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                order = Order.objects.get(id=order_id, user=request.user)
            except Order.DoesNotExist:
                return Response(
                    {"error": "Order not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Generate a unique transaction reference
            tx_ref = f"chapa-tx-{uuid.uuid4().hex}"

            # FIX: Include amount in URL parameters so it's available without authentication
            return_url_params = f"tx_ref={tx_ref}&order_id={order.id}&status=success&show_receipt=true&amount={order.total_amount}"
            return_url = f"{settings.FRONTEND_URL}/payment/result?{return_url_params}"

            # Prepare payload for Chapa API
            payload = {
                "amount": str(order.total_amount),
                "currency": "ETB",
                "email": order.customer_email,
                "first_name": order.customer_name.split()[0] if order.customer_name else "Customer",
                "last_name": " ".join(order.customer_name.split()[1:]) if order.customer_name and len(order.customer_name.split()) > 1 else "",
                "tx_ref": tx_ref,
                "callback_url": f"{settings.BASE_URL}/payments/webhook/",
                "return_url": return_url,
                "customization[title]": f"Payment for Order #{order.order_number}",
                "customization[description]": f"Payment for your order {order.order_number}"
            }

            if order.customer_phone:
                payload["phone_number"] = order.customer_phone

            # Headers with API key
            headers = {
                "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
                "Content-Type": "application/json",
            }

            # Initialize payment with Chapa API
            response = requests.post(settings.CHAPA_API_URL, json=payload, headers=headers)
            response_data = response.json()

            if response.status_code == 200 and response_data.get('status') == 'success':
                # Save transaction to DB
                PaymentTransaction.objects.create(
                    order=order,
                    tx_ref=tx_ref,
                    amount=order.total_amount,
                    email=order.customer_email,
                    first_name=payload['first_name'],
                    last_name=payload['last_name'],
                    phone_number=order.customer_phone,
                    user=request.user,
                    status='pending'
                )
                
                return Response({
                    "checkout_url": response_data['data']['checkout_url'],
                    "order_id": order.id,
                    "order_number": order.order_number,
                    "tx_ref": tx_ref,
                    "amount": str(order.total_amount),  # Also return amount in response
                    "status": "payment_initiated",
                    "message": "Payment initiated successfully. Redirecting to payment gateway."
                })
            else:
                # Update order status to failed
                order.status = 'failed'
                order.save()
                
                return Response(
                    {
                        "error": response_data.get('message', 'Payment initiation failed'),
                        "status": "payment_failed",
                        "message": "Failed to initiate payment. Please try again."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            return Response(
                {"error": str(e), "status": "error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        



@csrf_exempt
@require_http_methods(["GET", "POST"])  # Allow both GET and POST
def payment_webhook(request):
    """
    Handle both server-to-server webhook (POST) and user redirects (GET)
    """
    try:
        if request.method == 'POST':
            # Handle Chapa server webhook (POST)
            tx_ref = request.POST.get('tx_ref')
            if not tx_ref:
                return JsonResponse({"status": "error", "message": "Missing transaction reference"}, status=400)
            
            # Get the transaction
            try:
                transaction = PaymentTransaction.objects.get(tx_ref=tx_ref)
            except PaymentTransaction.DoesNotExist:
                return JsonResponse({"status": "error", "message": "Transaction not found"}, status=404)

            # Verify transaction with Chapa
            verify_url = f"{settings.CHAPA_VERIFY_URL}{tx_ref}"
            headers = {"Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"}
            response = requests.get(verify_url, headers=headers)
            response_data = response.json()

            if response.status_code == 200 and response_data.get('status') == 'success':
                # Update transaction status
                transaction.status = "completed"
                transaction.payment_method = response_data.get('data', {}).get('payment_type', '')
                transaction.save()

                # Update order status and reduce stock
                if transaction.order:
                    order = transaction.order
                    order.is_paid = True
                    # order.status = 'confirmed'
                    order.status = 'new'
                    order.save()
                    
                    # Reduce stock for order items
                    for order_item in order.items.all():
                        if order_item.product:
                            # For clothing products with size variants
                            try:
                                variant = ProductVariant.objects.get(
                                    product=order_item.product, 
                                    size=order_item.size
                                )
                                if variant.stock >= order_item.quantity:
                                    variant.stock -= order_item.quantity
                                    variant.save()
                            except ProductVariant.DoesNotExist:
                                print(f"Variant not found for {order_item.product.name} size {order_item.size}")
                        elif order_item.headwear_product:
                            # For headwear products
                            if order_item.headwear_product.stock >= order_item.quantity:
                                order_item.headwear_product.stock -= order_item.quantity
                                order_item.headwear_product.save()
                
                return JsonResponse({"status": "success"}, status=200)
            else:
                transaction.status = "failed"
                transaction.save()
                if transaction.order:
                    order = transaction.order
                    order.status = 'failed'
                    order.save()
                return JsonResponse(
                    {"status": "error", "message": response_data.get('message', 'Payment verification failed')},
                    status=400
                )

        elif request.method == 'GET':
            # Handle user redirect after payment (GET)
            tx_ref = request.GET.get('tx_ref') or request.GET.get('trx_ref')
            status_param = request.GET.get('status')
            
            print(f"Webhook GET received - tx_ref: {tx_ref}, status: {status_param}")
            print(f"All GET parameters: {dict(request.GET)}")
            
            if not tx_ref:
                return JsonResponse({"status": "error", "message": "Missing transaction reference"}, status=400)

            try:
                transaction = PaymentTransaction.objects.get(tx_ref=tx_ref)
            except PaymentTransaction.DoesNotExist:
                return JsonResponse({"status": "error", "message": "Transaction not found"}, status=404)

            # Check payment success indicators
            is_success = (
                status_param in ['success', 'successful', 'completed'] or
                request.GET.get('transaction_status') in ['success', 'successful', 'completed'] or
                request.GET.get('chapa_status') in ['success', 'successful', 'completed']
            )
            
            print(f"Payment success determination: {is_success}")

            # Update transaction status based on Chapa's response
            if is_success:
                transaction.status = 'completed'
                if transaction.order:
                    order = transaction.order
                    order.is_paid = True
                    # order.status = 'confirmed'
                    order.status = 'new'
                    order.save()
                    
                    # Reduce stock and clear cart
                    for order_item in order.items.all():
                        if order_item.product:
                            try:
                                variant = ProductVariant.objects.get(
                                    product=order_item.product, 
                                    size=order_item.size
                                )
                                if variant.stock >= order_item.quantity:
                                    variant.stock -= order_item.quantity
                                    variant.save()
                            except ProductVariant.DoesNotExist:
                                print(f"Variant not found for {order_item.product.name} size {order_item.size}")
                        elif order_item.headwear_product:
                            if order_item.headwear_product.stock >= order_item.quantity:
                                order_item.headwear_product.stock -= order_item.quantity
                                order_item.headwear_product.save()
                    
                    CartItem.objects.filter(cart__user=transaction.user).delete()
                    print(f"Order {order.id} marked as paid and cart cleared")
            else:
                transaction.status = 'failed'
                if transaction.order:
                    order = transaction.order
                    order.status = 'failed'
                    order.save()
                print(f"Order marked as failed")
            
            transaction.save()

            # Return transaction details for frontend
            return JsonResponse({
                "status": transaction.status,
                "tx_ref": transaction.tx_ref,
                "order_id": transaction.order.id if transaction.order else None,
                "order_number": transaction.order.order_number if transaction.order else None,
                "amount": str(transaction.amount) if transaction.amount else None,
                "is_paid": transaction.order.is_paid if transaction.order else False,
                "order_status": transaction.order.status if transaction.order else None
            }, status=200)

    except Exception as e:
        print(f"Error in payment webhook: {str(e)}")
        return JsonResponse({"status": "error", "message": "Internal server error"}, status=500)
    


# In payments/views.py - Update PaymentVerifyView
class PaymentVerifyView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        tx_ref = request.GET.get('tx_ref')
        if not tx_ref:
            return Response(
                {"error": "Transaction reference is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            transaction = PaymentTransaction.objects.get(tx_ref=tx_ref, user=request.user)
            
            # Verify with Chapa API
            verify_url = f"{settings.CHAPA_VERIFY_URL}{tx_ref}"
            headers = {"Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"}
            response = requests.get(verify_url, headers=headers)
            response_data = response.json()
            
            if response.status_code == 200 and response_data.get('status') == 'success':
                # Update transaction status if not already updated
                if transaction.status != 'completed':
                    transaction.status = 'completed'
                    if transaction.order:
                        transaction.order.is_paid = True
                        transaction.order.status = 'confirmed'
                        transaction.order.save()
                    transaction.save()
                
                # Return proper amount data
                return Response({
                    "status": "completed",
                    "tx_ref": transaction.tx_ref,
                    "order_id": transaction.order.id if transaction.order else None,
                    "order_number": transaction.order.order_number if transaction.order else None,
                    "amount": str(transaction.amount),  # Ensure this is properly formatted
                    "currency": "ETB",
                    "is_paid": True,
                    "verified": True,
                    "chapa_data": response_data.get('data', {})  # Include Chapa's response data
                })
            else:
                return Response({
                    "status": transaction.status,
                    "tx_ref": transaction.tx_ref,
                    "order_id": transaction.order.id if transaction.order else None,
                    "order_number": transaction.order.order_number if transaction.order else None,
                    "amount": str(transaction.amount) if transaction.amount else None,
                    "verified": False,
                    "message": "Payment verification failed"
                })
                
        except PaymentTransaction.DoesNotExist:
            return Response(
                {"error": "Transaction not found"},
                status=status.HTTP_404_NOT_FOUND
            )


def payment_success(request):
    # This is a fallback view, but we'll use the React component primarily
    tx_ref = request.GET.get('tx_ref')
    status = request.GET.get('status')
    
    context = {
        'success': status == 'successful',
        'message': 'Payment was successful!' if status == 'successful' else 'Payment was not successful',
        'tx_ref': tx_ref
    }
    
    return render(request, 'payments/payment_status.html', context)
