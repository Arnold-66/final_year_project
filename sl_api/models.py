from django.db import models
import os

class Sign(models.Model):
    word = models.CharField(max_length=255, unique=True)
    sigml_file = models.FileField(upload_to='sigml/')
    category = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.word

    def get_filename(self):
        if self.sigml_file:
            return os.path.basename(self.sigml_file.name)
        return "-"

    class Meta:
        ordering = ['word']
