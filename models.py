from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.FloatField(default=0.0)
    last_click = models.DateTimeField(null=True, blank=True)
    clicks_today = models.IntegerField(default=0)
    last_click_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - Balance: ?{self.balance}"

class WithdrawalRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Success', 'Success'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()

    # Dono lines mein max_length bilkul perfect set kar diya hai:
    upi_or_paytm = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - ?{self.amount} ({self.status})"



class Task(models.Model):
    app_name = models.CharField(max_length=100)
    icon = models.ImageField(upload_to='tasks/', null=True, blank=True)
    affiliate_link = models.URLField(max_length=500)
    reward_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.app_name