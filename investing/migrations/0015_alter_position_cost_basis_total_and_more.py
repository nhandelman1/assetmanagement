# Generated by Django 4.2.5 on 2023-10-26 23:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investing', '0014_alter_position_cost_basis_total_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='position',
            name='cost_basis_total',
            field=models.DecimalField(decimal_places=2, max_digits=12),
        ),
        migrations.AlterField(
            model_name='position',
            name='market_value',
            field=models.DecimalField(decimal_places=2, max_digits=12),
        ),
    ]