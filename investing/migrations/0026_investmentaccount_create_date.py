# Generated by Django 4.2.5 on 2023-11-04 19:33

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investing', '0025_alter_closedposition_cost_basis_price_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='investmentaccount',
            name='create_date',
            field=models.DateField(default=datetime.date(2020, 1, 1)),
            preserve_default=False,
        ),
    ]