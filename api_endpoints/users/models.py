from django.db import models
from django.contrib.auth.models import User

class Alert(models.Model):
    STATE_CHOICES = [
        ('created', 'Created'),
        ('triggered', 'Triggered'),
        ('deleted', 'Deleted'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    target_price = models.DecimalField(max_digits=10, decimal_places=2)
    trigger_condition = models.CharField(
        max_length=10,
        choices=[('above', 'Above'), ('below', 'Below')],
        default='above'
    )
    email = models.EmailField()
    state = models.CharField(
        max_length=10,
        choices=STATE_CHOICES,
        default='created',
        editable=False  # Make this field non-editable by the user
    )

    class Meta:
        indexes = [
            models.Index(fields=['target_price']),
            models.Index(fields=['state']),
        ]

    def __str__(self):
        return f'Alert with target price {self.target_price} and state {self.state}'
