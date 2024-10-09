from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ACCOUNT_TIERS = (
        ('free', 'Free'),
        ('premium', 'Premium'),
    )
    account_tier = models.CharField(max_length=10, choices=ACCOUNT_TIERS, default='free')
    queries_this_month = models.IntegerField(default=0)
    last_query_reset = models.DateTimeField(auto_now_add=True)

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='rag_app_user_set',
        related_query_name='rag_app_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='rag_app_user_set',
        related_query_name='rag_app_user',
    )