from django.db import models

# Create your models here.


class JobOfferInfo(models.Model):

    offer_id = models.CharField(unique=True, max_length=250, null=True, blank=True)
    offer_link = models.CharField(max_length=250, null=True, blank=True)
    offer_name = models.CharField(max_length=250, null=True, blank=True)
    job_type = models.CharField(max_length=250, null=True, blank=True)
    salary = models.CharField(max_length=250, null=True, blank=True)
    tier = models.CharField(max_length=250, null=True, blank=True)
    duration = models.CharField(max_length=250, null=True, blank=True)
    date_posted = models.DateTimeField(null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=250, null=True, blank=True)
    connects_to_apply = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.offer_name

    class Meta:
        verbose_name = 'Job offer'
        verbose_name_plural = 'Job offers'

class Page(models.Model):
    link = models.CharField(max_length=255)
    status = models.BooleanField(default=False)


class SearchQuery(models.Model):
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Query'
        verbose_name_plural = 'Queries'