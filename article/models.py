from django.db import models

# Create your models here.

# import User model with build
from django.contrib.auth.models import User

# import django timezone
from django.utils import timezone

class ArticlePost(models.Model):
    # author , on_delete
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    # title max_length
    title = models.CharField(max_length=100)

    # content Stored Text
    body = models.TextField()

    # created ,default write time
    created = models.DateTimeField(default=timezone.now)

    # updated ,default update time
    updated = models.DateTimeField(auto_now=True)

    # marked is deleted
    is_deleted = models.BooleanField(default=False)

    # meta data
    class Meta:
        # order by reverse
        ordering = ['-created']

    def __str__(self):
        # return self.title
        return self.title

    def delete(self, using=None, keep_parents=False):
        # rewrite delete fun, psundo delete
        self.is_deleted = True
        self.save()

    def restore(self):
        # providers recover deleted data fun
        self.is_deleted = False
        self.save()

class ArticleQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=False)

    def delete(self):
        return self.filter(is_deleted=True)

class ArticleManager(models.Manager):
    def get_queryset(self):
        return ArticleQuerySet(self.model, using=self._db).filter(is_deleted=False)
