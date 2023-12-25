# Generated by Django 4.2.5 on 2023-11-11 21:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investing', '0033_alter_transaction_action_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='position',
            name='cost_basis_price',
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=9, null=True),
        ),
        migrations.AlterField(
            model_name='position',
            name='enter_price',
            field=models.DecimalField(decimal_places=4, max_digits=9),
        ),
        migrations.AlterField(
            model_name='position',
            name='enter_price_net',
            field=models.DecimalField(decimal_places=4, max_digits=9),
        ),
        migrations.AlterField(
            model_name='position',
            name='eod_price',
            field=models.DecimalField(decimal_places=4, max_digits=9),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=9, null=True),
        ),
    ]