# Generated migration for transaction tracking fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0006_remove_order_customer_remove_order_is_completed_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='transaction_reference',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='order',
            name='transaction_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending'),
                    ('completed', 'Completed'),
                    ('cancelled', 'Cancelled'),
                    ('failed', 'Failed'),
                ],
                default='pending',
                max_length=20,
            ),
        ),
    ]
