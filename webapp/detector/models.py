from django.db import models

class LogEntry(models.Model):
    log_line = models.TextField()
    prediction = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return self.log_line[:50]