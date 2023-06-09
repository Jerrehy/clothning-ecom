# Generated by Django 4.2.1 on 2023-06-03 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_remove_product_specs'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productattribute',
            name='image',
        ),
        migrations.RemoveField(
            model_name='productattribute',
            name='price',
        ),
        migrations.AddField(
            model_name='product',
            name='image',
            field=models.ImageField(null=True, upload_to='product_imgs/'),
        ),
        migrations.AddField(
            model_name='product',
            name='price',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
