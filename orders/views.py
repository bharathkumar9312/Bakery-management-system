from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.utils.dateparse import parse_datetime, parse_date
from django.utils import timezone
from decimal import Decimal
from django.http import JsonResponse
from invoices.models import Invoice, InvoiceItem
from products.models import Product
from customers.models import Customers
from .models import Order, OrderItem
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages 

def create_order_view(request):
    products_for_js = Product.objects.filter(status=True)

    if request.method == 'POST':
        customer_phone = request.POST.get('customer_phone','').strip()
        customer_name = request.POST.get('customer_name','').strip()

        if not customer_phone:
            messages.error(request, "Customer phone number is required.")
            return render(request, 'create_order.html', {'products': products_for_js})
        if not customer_name:
            messages.error(request, "Customer name is required.")
            return render(request, 'create_order.html', {'products': products_for_js, 'customer_phone': customer_phone})

        customer, created = Customers.objects.get_or_create(
            Phone_number=customer_phone,
            defaults={'name': customer_name}
        )
        if not created and customer.name != customer_name:
            customer.name = customer_name
            customer.save()

        product_ids = request.POST.getlist('product_id[]')
        quantities_str = request.POST.getlist('quantity[]')
        item_prices_str = request.POST.getlist('item_price[]')
        item_size_names = request.POST.getlist('item_size_name[]')

        if not product_ids:
            messages.error(request, "No products were selected for the order.")
            return render(request, 'create_order.html', {'products': products_for_js})

        if not (len(product_ids) == len(quantities_str) == len(item_prices_str) == len(item_size_names)):
            messages.error(request, "Mismatch in submitted product data. Please try again.")
            return render(request, 'create_order.html', {'products': products_for_js})

        calculated_items_total_float = 0.0 # Total from items only
        order_items_to_create = []
        
        for i in range(len(product_ids)):
            pid = product_ids[i]
            qty_s = quantities_str[i]
            price_s = item_prices_str[i] 
            size_name = item_size_names[i]
            
            try:
                product_obj = Product.objects.get(id=pid)
                quantity = int(qty_s)
                actual_item_unit_price_float = float(price_s) 

                if quantity <= 0:
                    messages.error(request, f"Quantity for {product_obj.name} ({size_name}) must be positive.")
                    return render(request, 'create_order.html', {'products': products_for_js})

                line_item_total_float = actual_item_unit_price_float * quantity
                calculated_items_total_float += line_item_total_float # Accumulate item total
                
                order_items_to_create.append({
                    'product': product_obj,
                    'quantity': quantity,
                    'price_float': actual_item_unit_price_float,
                    'total_float': line_item_total_float,
                    'size_name': size_name,
                })
            except Product.DoesNotExist:
                messages.error(request, f"Product with ID {pid} not found.")
                return render(request, 'create_order.html', {'products': products_for_js})
            except (ValueError, TypeError) as e:
                messages.error(request, f'Error processing order item: {e}')
                return render(request, 'create_order.html', {'products': products_for_js})

        is_customized = request.POST.get('customized_option') == 'Yes'
        whatsapp = request.POST.get('whatsapp_number', '').strip()
        
        # Get customization charge. If you add an input field for this in HTML:
        # Make sure its name is 'customization_charge'
        customization_charge_str = request.POST.get('customization_charge', '0').strip()
        try:
            customization_charge_float = float(customization_charge_str) if customization_charge_str else 0.0
        except ValueError:
            messages.error(request, "Invalid customization charge value.")
            # Pass back relevant form data
            return render(request, 'create_order.html', {'products': products_for_js, 'customer_phone': customer_phone, 'customer_name': customer_name})


        # THE FIX: Add customization_charge_float to the overall total
        calculated_order_total_float = calculated_items_total_float + customization_charge_float

        message = request.POST.get('message', '').strip()
        advance_amount_str = request.POST.get('advance_amount', '0').strip()
        advance_amount_float = float(advance_amount_str) if advance_amount_str else 0.0
        payment_method_for_advance = request.POST.get('payment_method', 'Cash')

        delivery_str = request.POST.get('delivery_time')
        delivery_datetime = None
        if delivery_str:
            try:
                delivery_datetime = parse_datetime(delivery_str)
                if delivery_datetime:
                    delivery_datetime = timezone.make_aware(delivery_datetime)
            except ValueError:
                messages.error(request, "Invalid delivery date/time format.")
                return render(request, 'create_order.html', {'products': products_for_js})
        else:
            messages.error(request, "Delivery date and time are required.")
            return render(request, 'create_order.html', {'products': products_for_js})

        if advance_amount_float > calculated_order_total_float:
            messages.error(request, "Advance amount cannot be greater than the total order amount.")
            return render(request, 'create_order.html', {'products': products_for_js})

        final_order_total_int = round(calculated_order_total_float)
        advance_amount_int = round(advance_amount_float)
        customization_charge_int = round(customization_charge_float)

        with transaction.atomic():
            order = Order.objects.create(
                customer=customer,
                total_amount=final_order_total_int, # This now includes customization charge
                is_customized=is_customized,
                whatsapp_number=whatsapp if is_customized else '',
                customization_charge=customization_charge_int, # Store the charge itself
                message=message,
                delivery_datetime=delivery_datetime,
                advance_amount=advance_amount_int,
                payment_method=payment_method_for_advance if advance_amount_int > 0 else None,
            )

            for item_data in order_items_to_create:
                OrderItem.objects.create(
                    order=order,
                    product=item_data['product'],
                    quantity=item_data['quantity'],
                    price=round(item_data['price_float']),
                    total=round(item_data['total_float']),
                    size_name=item_data['size_name'] # Assuming you added size_name to OrderItem model
                )
            
        messages.success(request, f"Order #{order.id} placed successfully!")
        return redirect('order_receipt', order_id=order.id)

    return render(request, 'create_order.html', {'products': products_for_js})

def order_success_view(request):
    return render(request, 'order_success.html')


def order_receipt(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = order.orderitem_set.all()
    total_amount = Decimal(str(order.total_amount))
    remaining_balance = total_amount - order.advance_amount
    context = {
        'order': order,
        'order_items': order_items,
        'remaining_balance': remaining_balance,
        "copies": ["Customer Copy", "Shop Copy"],
    }
    return render(request, 'order_receipt.html', context)


def order_list_view(request):
    orders = Order.objects.all().order_by('-date')

    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    phone = request.GET.get('phone')
    order_id = request.GET.get('order_id') 

    if from_date:
        orders = orders.filter(date__date__gte=parse_date(from_date))
    if to_date:
        orders = orders.filter(date__date__lte=parse_date(to_date))
    if phone:
        orders = orders.filter(customer__Phone_number__icontains=phone)
    if order_id:
        try:
            orders = orders.filter(id=order_id)
        except ValueError:
            pass

    context = {
        'orders': orders,
        'from_date': from_date,
        'to_date': to_date,
        'phone': phone,
        'amount': order_id,
    }
    return render(request, 'order_list.html', context)

@csrf_exempt
def toggle_delivery_status(request, order_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)
    
    try:
        order = Order.objects.get(id=order_id)
        
        with transaction.atomic():
            order.status = not order.status
            order.save()
            
            invoice_data = None
            if order.status and not order.invoice:
                invoice = Invoice.objects.create(
                    customer=order.customer,
                    date=timezone.now(),
                    total_amount=order.total_amount,
                    grand_total=order.total_amount,
                    payment_method=order.payment_method
                )
                
                for item in order.orderitem_set.all():
                    InvoiceItem.objects.create(
                        invoice=invoice,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.price,
                        total=item.total
                    )
                
                order.invoice = invoice
                order.save()
                
            
            return JsonResponse({
                'success': True,
                'status': order.status,
                
            })
            
    except Order.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Order not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)