from django.shortcuts import render,redirect, get_object_or_404
from django.http import JsonResponse
from .models import Customers
from .forms import CustomersForm


def customers_list(request):
    customers = Customers.objects.all()
    return render(request, 'customers/customers_list.html', {'customers': customers})

def customers_create(request):
    form = CustomersForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('customers_list')
    return render(request, 'customers/customers_form.html', {'form': form})

# Delete Customers
def customers_delete(request, pk):
    customers = get_object_or_404(Customers, pk=pk)
    if request.method == 'POST':
        customers.delete()
        return redirect('customers_list')
    return render(request, 'customers/customers_confirm_delete.html', {'customers': customers})

def customer_search_api(request):
    phone = request.GET.get('Phone_number')
    customer = Customers.objects.filter(Phone_number=phone).first()
    if customer:
        return JsonResponse({'exists': True, 'name': customer.name})
    else:
        return JsonResponse({'exists': False})
