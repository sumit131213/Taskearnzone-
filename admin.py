from django.contrib import admin
from .models import UserProfile, WithdrawalRequest, Task

admin.site.register(UserProfile)
admin.site.register(WithdrawalRequest)
admin.site.register(Task)