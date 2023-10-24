# Generated by Django 4.2.5 on 2023-10-19 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SecurityMaster',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('my_id', models.CharField(max_length=30, unique=True)),
                ('ticker', models.CharField(max_length=30, unique=True)),
                ('asset_class', models.CharField(choices=[('BOND', 'BOND'), ('EQUITY', 'EQUITY'), ('OPTION', 'OPTION')], max_length=20)),
                ('asset_subclass', models.CharField(choices=[('COMMON_STOCK', 'COMMON_STOCK'), ('CORP_BOND', 'CORP_BOND'), ('EQUITY_OPTION', 'EQUITY_OPTION'), ('ETF', 'ETF'), ('GOV_BOND', 'GOV_BOND'), ('INDEX_OPTION', 'INDEX_OPTION'), ('MUNI_BOND', 'MUNI_BOND')], max_length=20)),
            ],
        ),
    ]