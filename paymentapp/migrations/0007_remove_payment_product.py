# Generated by Django 4.2.3 on 2023-07-14 18:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('paymentapp', '0006_payment_user_alter_payment_created_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='product',
        ),
    ]