# Generated by Django 4.0.3 on 2022-12-15 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apiApp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product_data',
            name='category',
            field=models.TextField(default='rings'),
            preserve_default=False,
        ),
    ]
