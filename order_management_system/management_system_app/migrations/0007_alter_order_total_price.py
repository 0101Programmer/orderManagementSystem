# Generated by Django 5.1.6 on 2025-03-07 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management_system_app', '0006_alter_order_items'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='total_price',
            field=models.FloatField(help_text='Общая стоимость заказа, которая вычисляется автоматически.'),
        ),
    ]
