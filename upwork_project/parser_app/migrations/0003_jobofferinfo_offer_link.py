# Generated by Django 4.2.2 on 2023-06-27 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parser_app', '0002_jobofferinfo_offer_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobofferinfo',
            name='offer_link',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
