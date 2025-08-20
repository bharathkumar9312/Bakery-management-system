# invoices/models.py
from django.db import models
from products.models import Product
from customers.models import Customers  

class Invoice(models.Model):

    
    customer = models.ForeignKey(Customers, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    total_amount = models.IntegerField(null=True, blank=True)
    grand_total = models.IntegerField(null=True, blank=True)
    PAYMENT_CHOICES = [
        ('Cash', 'Cash'),
        ('GPay', 'GPay'),
        ('Card', 'Card'),
    ]
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='Cash')
    def __str__(self):
        return f"Invoice #{self.id} - {self.customer.name}"

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.IntegerField()  # single item price
    total = models.IntegerField()  # price * quantity
    size_name = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        if self.size_name and self.size_name != 'Standard':
            return f"{self.product.name} ({self.size_name}) x{self.quantity}"
        return f"{self.product.name} x{self.quantity}"
    
class DailySale(models.Model):
    date = models.DateField(unique=True)
    total_amount = models.IntegerField(default=0)
    total_orders = models.PositiveIntegerField(default=0)
    total_items_sold = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.date} - ₹{self.total_amount}"