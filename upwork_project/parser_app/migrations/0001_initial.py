# Generated by Django 4.2.2 on 2023-06-27 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='JobOfferInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('job_type', models.CharField(blank=True, max_length=250, null=True)),
                ('salary', models.CharField(blank=True, max_length=250, null=True)),
                ('tier', models.CharField(blank=True, max_length=250, null=True)),
                ('duration', models.CharField(blank=True, max_length=250, null=True)),
                ('date_posted', models.DateTimeField(blank=True, null=True)),
                ('text', models.TextField(blank=True, null=True)),
                ('category', models.CharField(blank=True, max_length=250, null=True)),
            ],
            options={
                'verbose_name': 'Job offer',
                'verbose_name_plural': 'Job offers',
            },
        ),
    ]
