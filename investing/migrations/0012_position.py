# Generated by Django 4.2.5 on 2023-10-26 22:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('investing', '0011_investmentaccount_taxable'),
    ]

    operations = [
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.DecimalField(decimal_places=4, max_digits=12)),
                ('close_price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('market_value', models.DecimalField(decimal_places=2, max_digits=12)),
                ('cost_basis_avg', models.DecimalField(decimal_places=2, max_digits=8)),
                ('cost_basis_total', models.DecimalField(decimal_places=2, max_digits=12)),
                ('investment_account', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='investing.investmentaccount')),
                ('security', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='investing.securitymaster')),
            ],
        ),
    ]