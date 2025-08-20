
from django.db import models
from products.models import Product
from customers.models import Customers  

class Order(models.Model):
    customer = models.ForeignKey(Customers, on_delete=models.SET_NULL, null=True, blank=True)
    invoice = models.OneToOneField('invoices.Invoice', on_delete=models.SET_NULL, null=True, blank=True) 
    date = models.DateTimeField(auto_now_add=True)
    total_amount = models.IntegerField(null=True, blank=True)
    is_customized = models.BooleanField(default=False)
    whatsapp_number = models.CharField(max_length=15, blank=True, null=True)
    customization_charge = models.IntegerField(default=0)
    message = models.TextField(blank=True, null=True)
    delivery_datetime = models.DateTimeField()
    advance_amount = models.IntegerField(default=0)
    

    PAYMENT_CHOICES = [
        ('Cash', 'Cash'),
        ('GPay', 'GPay'),
        ('Card', 'Card'),
    ]
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='Cash')
    status = models.BooleanField(default=False) 
    def __str__(self):
        return f"Invoice #{self.id} - {self.customer.name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.IntegerField()  # single item price
    total = models.IntegerField()  # price * quantity
    size_name = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        if self.size_name and self.size_name != "Standard":
            return f"{self.product.name} ({self.size_name}) x{self.quantity}"
        return f"{self.product.name} x{self.quantity}"
