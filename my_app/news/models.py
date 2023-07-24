from django.db import models
from django.conf import settings

class NewStatusChoises(models.TextChoices):
    """Статусы новостей"""
    OPEN = "OPEN", "Открыто"
    CLOSED = "CLOSED", "Закрыто"
    DRAFT = 'DRAFT', 'Черновик'

class News(models.Model):
    title = models.TextField()
    description = models.TextField(default='')
    status = models.TextField(choices=NewStatusChoises.choices,default=NewStatusChoises.OPEN)
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='my_news')
    created_at = models.DateTimeField(auto_now_add=True)
    like = models.ManyToManyField(settings.AUTH_USER_MODEL, through='UserNewRelation', related_name='likes')
    
class Comments(models.Model):
    post = models.ForeignKey(News, on_delete=models.CASCADE, related_name='comments', blank=True)
    description = models.TextField(default='')
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,)
    created_at = models.DateTimeField(auto_now_add=True)
    
class UserNewRelation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    news = models.ForeignKey(News, on_delete=models.CASCADE)
    like = models.BooleanField(default=False)