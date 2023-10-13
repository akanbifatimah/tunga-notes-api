from django.db import models
from datetime import datetime
# Create your models here.


class Note(models.Model):
    title = models.CharField(max_length=100,unique=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateField(null=True, blank=True)
    
    STATUS_CHOICES = [
        ('unfinished', 'Unfinished'),
        ('overdue', 'Overdue'),
        ('done', 'Done'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Done')
    def save(self, *args, **kwargs):
        self.status = self.differentiate_status(self.due_date)
        super().save(*args, **kwargs)

# sort notes by due_date
    def differentiate_status(self, due_date):
        today = datetime.now().date()

        if due_date is None:
            return 'unfinished'
        elif due_date < today:
            return 'overdue'
        else:
            return 'done'
        
    def __str__(self):
        return self.title

