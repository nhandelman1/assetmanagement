# Generated by Django 4.2.5 on 2023-09-18 19:01

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import realestate.models.depreciationbilldata
import realestate.models.electricbilldata
import realestate.models.electricdata
import realestate.models.mortgagebilldata
import realestate.models.natgasbilldata
import realestate.models.natgasdata
import realestate.models.simplebilldata
import realestate.models.solarbilldata


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MySunpowerHourlyData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dt', models.DateTimeField(unique=True)),
                ('solar_kwh', models.DecimalField(decimal_places=2, max_digits=5)),
                ('home_kwh', models.DecimalField(decimal_places=2, max_digits=5)),
            ],
        ),
        migrations.CreateModel(
            name='RealEstate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(choices=[('10 Wagon Ln Centereach NY 11720', '10 Wagon Ln Centereach NY 11720'), ('10 Wagon Ln Apt 1 Centereach NY 11720', '10 Wagon Ln Apt 1 Centereach NY 11720')], max_length=70, unique=True)),
                ('street_num', models.CharField(max_length=10)),
                ('street_name', models.CharField(max_length=20)),
                ('apt', models.CharField(blank=True, max_length=10, null=True)),
                ('city', models.CharField(max_length=20)),
                ('state', models.CharField(max_length=2, validators=[django.core.validators.RegexValidator('^[A-Z]{2}$')])),
                ('zip_code', models.CharField(max_length=5, validators=[django.core.validators.RegexValidator('^[0-9]{5}$')])),
                ('bill_tax_related', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='ServiceProvider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('provider', models.CharField(choices=[('BigCityPlumbingHeating-REP', 'BigCityPlumbingHeating-REP'), ('Depreciation-DEP', 'Depreciation-DEP'), ('HomeDepot-SUP', 'HomeDepot-SUP'), ('HandymenOfAllTrades-REP', 'HandymenOfAllTrades-REP'), ('KnockoutPestControl-CM', 'KnockoutPestControl-CM'), ('MorganStanley-MI', 'MorganStanley-MI'), ('NarragansettBay-INS', 'NarragansettBay-INS'), ('NationalGrid-UTI', 'NationalGrid-UTI'), ('NicholasHandelman', 'NicholasHandelman'), ('OceanHarbor-INS', 'OceanHarbor-INS'), ('OptimumCable-UTI', 'OptimumCable-UTI'), ('OptimumInternet-UTI', 'OptimumInternet-UTI'), ('PSEG-UTI', 'PSEG-UTI'), ('SCWA-UTI', 'SCWA-UTI'), ('SuffolkCounty-TAX', 'SuffolkCounty-TAX'), ('Walmart-SUP', 'Walmart-SUP'), ('10WagonLnAptTenant-INC', '10WagonLnAptTenant-INC'), ('10WagonLnSunpower', '10WagonLnSunpower'), ('WolfPlumbing-REP', 'WolfPlumbing-REP'), ('VerizonInternet-UTI', 'VerizonInternet-UTI'), ('YoutubeTV-UTI', 'YoutubeTV-UTI')], max_length=100, unique=True)),
                ('tax_category', models.CharField(choices=[('Depreciation', 'Depreciation'), ('CleaningMaintenance', 'CleaningMaintenance'), ('Income', 'Income'), ('Insurance', 'Insurance'), ('MortgageInterest', 'MortgageInterest'), ('None', 'None'), ('Repairs', 'Repairs'), ('Supplies', 'Supplies'), ('Taxes', 'Taxes'), ('Utilities', 'Utilities')], max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='SolarBillData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('total_cost', models.DecimalField(decimal_places=2, max_digits=8)),
                ('tax_rel_cost', models.DecimalField(decimal_places=2, max_digits=8)),
                ('paid_date', models.DateField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('solar_kwh', models.DecimalField(decimal_places=2, max_digits=7)),
                ('home_kwh', models.DecimalField(decimal_places=2, max_digits=7)),
                ('actual_costs', models.DecimalField(decimal_places=2, max_digits=8)),
                ('oc_bom_basis', models.DecimalField(decimal_places=2, max_digits=8)),
                ('oc_pnl_pct', models.DecimalField(decimal_places=2, max_digits=4)),
                ('oc_pnl', models.DecimalField(decimal_places=2, max_digits=8)),
                ('oc_eom_basis', models.DecimalField(decimal_places=2, max_digits=8)),
                ('real_estate', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='realestate.realestate')),
                ('service_provider', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='realestate.serviceprovider', validators=[realestate.models.solarbilldata.SolarBillData.validate_service_provider])),
            ],
        ),
        migrations.CreateModel(
            name='SimpleBillData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('total_cost', models.DecimalField(decimal_places=2, max_digits=8)),
                ('tax_rel_cost', models.DecimalField(decimal_places=2, max_digits=8)),
                ('paid_date', models.DateField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('real_estate', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='realestate.realestate')),
                ('service_provider', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='realestate.serviceprovider', validators=[realestate.models.simplebilldata.SimpleBillData.validate_service_provider])),
            ],
        ),
        migrations.CreateModel(
            name='RealPropertyValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item', models.CharField(max_length=100)),
                ('purchase_date', models.DateField()),
                ('disposal_date', models.DateField(blank=True, null=True)),
                ('cost_basis', models.DecimalField(decimal_places=2, max_digits=11)),
                ('dep_class', models.CharField(choices=[('None-None-None-None', 'None-None-None-None'), ('GDS-RRP-SL-MM', 'GDS-RRP-SL-MM'), ('GDS-YEAR5-SL-MM', 'GDS-YEAR5-SL-MM')], max_length=100)),
                ('notes', models.TextField(blank=True, null=True)),
                ('real_estate', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='realestate.realestate')),
            ],
        ),
        migrations.CreateModel(
            name='NatGasData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month_date', models.DateField()),
                ('month_year', models.CharField(max_length=6)),
                ('bsc_therms', models.DecimalField(decimal_places=1, max_digits=3)),
                ('bsc_rate', models.DecimalField(decimal_places=4, max_digits=6)),
                ('next_therms', models.DecimalField(decimal_places=1, max_digits=4)),
                ('next_rate', models.DecimalField(decimal_places=4, max_digits=5)),
                ('over_rate', models.DecimalField(decimal_places=4, max_digits=5)),
                ('dra_rate', models.DecimalField(blank=True, decimal_places=6, max_digits=7, null=True)),
                ('wna_low_rate', models.DecimalField(blank=True, decimal_places=6, max_digits=7, null=True)),
                ('wna_high_rate', models.DecimalField(blank=True, decimal_places=6, max_digits=7, null=True)),
                ('sbc_rate', models.DecimalField(blank=True, decimal_places=6, max_digits=7, null=True)),
                ('tac_rate', models.DecimalField(blank=True, decimal_places=6, max_digits=7, null=True)),
                ('bc_rate', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('ds_nysls_rate', models.DecimalField(blank=True, decimal_places=6, max_digits=7, null=True)),
                ('ds_nysst_rate', models.DecimalField(blank=True, decimal_places=4, max_digits=5, null=True)),
                ('gs_rate', models.DecimalField(decimal_places=6, max_digits=7)),
                ('ss_nysls_rate', models.DecimalField(blank=True, decimal_places=6, max_digits=7, null=True)),
                ('ss_nysst_rate', models.DecimalField(blank=True, decimal_places=4, max_digits=5, null=True)),
                ('pbc_rate', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('real_estate', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='realestate.realestate')),
                ('service_provider', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='realestate.serviceprovider', validators=[realestate.models.natgasdata.NatGasData.validate_service_provider])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='NatGasBillData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('total_cost', models.DecimalField(decimal_places=2, max_digits=8)),
                ('tax_rel_cost', models.DecimalField(decimal_places=2, max_digits=8)),
                ('paid_date', models.DateField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('is_actual', models.BooleanField()),
                ('total_therms', models.PositiveSmallIntegerField()),
                ('saved_therms', models.PositiveSmallIntegerField()),
                ('bsc_therms', models.DecimalField(decimal_places=1, max_digits=3)),
                ('bsc_cost', models.DecimalField(decimal_places=2, max_digits=5)),
                ('next_therms', models.DecimalField(decimal_places=1, max_digits=4)),
                ('next_rate', models.DecimalField(decimal_places=4, max_digits=5)),
                ('next_cost', models.DecimalField(decimal_places=2, max_digits=5)),
                ('over_therms', models.DecimalField(blank=True, decimal_places=1, max_digits=4, null=True)),
                ('over_rate', models.DecimalField(blank=True, decimal_places=4, max_digits=5, null=True)),
                ('over_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('dra_rate', models.DecimalField(blank=True, decimal_places=6, max_digits=7, null=True)),
                ('dra_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('sbc_rate', models.DecimalField(blank=True, decimal_places=6, max_digits=7, null=True)),
                ('sbc_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('tac_rate', models.DecimalField(blank=True, decimal_places=6, max_digits=7, null=True)),
                ('tac_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('bc_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('ds_nysls_rate', models.DecimalField(blank=True, decimal_places=6, max_digits=7, null=True)),
                ('ds_nysls_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('ds_nysst_rate', models.DecimalField(blank=True, decimal_places=4, max_digits=5, null=True)),
                ('ds_nysst_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('ds_total_cost', models.DecimalField(decimal_places=2, max_digits=6)),
                ('gs_rate', models.DecimalField(decimal_places=6, max_digits=7)),
                ('gs_cost', models.DecimalField(decimal_places=2, max_digits=6)),
                ('ss_nysls_rate', models.DecimalField(blank=True, decimal_places=6, max_digits=7, null=True)),
                ('ss_nysls_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('ss_nysst_rate', models.DecimalField(blank=True, decimal_places=4, max_digits=5, null=True)),
                ('ss_nysst_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('ss_total_cost', models.DecimalField(decimal_places=2, max_digits=6)),
                ('pbc_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('oca_total_cost', models.DecimalField(decimal_places=2, max_digits=5)),
                ('real_estate', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='realestate.realestate')),
                ('service_provider', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='realestate.serviceprovider', validators=[realestate.models.natgasbilldata.NatGasBillData.validate_service_provider])),
            ],
        ),
        migrations.CreateModel(
            name='MortgageBillData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('total_cost', models.DecimalField(decimal_places=2, max_digits=8)),
                ('tax_rel_cost', models.DecimalField(decimal_places=2, max_digits=8)),
                ('paid_date', models.DateField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('outs_prin', models.DecimalField(decimal_places=2, max_digits=10)),
                ('esc_bal', models.DecimalField(decimal_places=2, max_digits=8)),
                ('prin_pmt', models.DecimalField(decimal_places=2, max_digits=7)),
                ('int_pmt', models.DecimalField(decimal_places=2, max_digits=7)),
                ('esc_pmt', models.DecimalField(decimal_places=2, max_digits=7)),
                ('other_pmt', models.DecimalField(decimal_places=2, max_digits=7)),
                ('real_estate', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='realestate.realestate')),
                ('service_provider', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='realestate.serviceprovider', validators=[realestate.models.mortgagebilldata.MortgageBillData.validate_service_provider])),
            ],
        ),
        migrations.CreateModel(
            name='EstimateNote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note_type', models.CharField(max_length=20)),
                ('note', models.TextField()),
                ('note_order', models.PositiveSmallIntegerField()),
                ('real_estate', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='realestate.realestate')),
                ('service_provider', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='realestate.serviceprovider')),
            ],
        ),
        migrations.CreateModel(
            name='ElectricData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month_date', models.DateField()),
                ('month_year', models.CharField(max_length=6)),
                ('first_kwh', models.PositiveSmallIntegerField()),
                ('first_rate', models.DecimalField(decimal_places=4, max_digits=5)),
                ('next_rate', models.DecimalField(decimal_places=4, max_digits=5)),
                ('mfc_rate', models.DecimalField(blank=True, decimal_places=6, max_digits=7, null=True)),
                ('psc_rate', models.DecimalField(blank=True, decimal_places=6, max_digits=7, null=True)),
                ('der_rate', models.DecimalField(blank=True, decimal_places=6, max_digits=7, null=True)),
                ('dsa_rate', models.DecimalField(blank=True, decimal_places=6, max_digits=7, null=True)),
                ('rda_rate', models.DecimalField(blank=True, decimal_places=6, max_digits=7, null=True)),
                ('nysa_rate', models.DecimalField(blank=True, decimal_places=6, max_digits=7, null=True)),
                ('rbp_rate', models.DecimalField(blank=True, decimal_places=6, max_digits=7, null=True)),
                ('spta_rate', models.DecimalField(blank=True, decimal_places=6, max_digits=7, null=True)),
                ('real_estate', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='realestate.realestate')),
                ('service_provider', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='realestate.serviceprovider', validators=[realestate.models.electricdata.ElectricData.validate_service_provider])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ElectricBillData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('total_cost', models.DecimalField(decimal_places=2, max_digits=8)),
                ('tax_rel_cost', models.DecimalField(decimal_places=2, max_digits=8)),
                ('paid_date', models.DateField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('is_actual', models.BooleanField()),
                ('total_kwh', models.PositiveSmallIntegerField()),
                ('eh_kwh', models.PositiveSmallIntegerField()),
                ('bank_kwh', models.PositiveIntegerField()),
                ('bs_rate', models.DecimalField(decimal_places=2, max_digits=4)),
                ('bs_cost', models.DecimalField(decimal_places=2, max_digits=6)),
                ('first_kwh', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('first_rate', models.DecimalField(blank=True, decimal_places=4, max_digits=5, null=True)),
                ('first_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('next_kwh', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('next_rate', models.DecimalField(blank=True, decimal_places=4, max_digits=5, null=True)),
                ('next_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('cbc_rate', models.DecimalField(blank=True, decimal_places=4, max_digits=5, null=True)),
                ('cbc_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('mfc_rate', models.DecimalField(blank=True, decimal_places=6, max_digits=7, null=True)),
                ('mfc_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('dsc_total_cost', models.DecimalField(decimal_places=2, max_digits=6)),
                ('psc_rate', models.DecimalField(blank=True, decimal_places=6, max_digits=7, null=True)),
                ('psc_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('psc_total_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('der_rate', models.DecimalField(blank=True, decimal_places=6, max_digits=7, null=True)),
                ('der_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('dsa_rate', models.DecimalField(blank=True, decimal_places=6, max_digits=7, null=True)),
                ('dsa_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('rda_rate', models.DecimalField(blank=True, decimal_places=6, max_digits=7, null=True)),
                ('rda_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('nysa_rate', models.DecimalField(blank=True, decimal_places=6, max_digits=7, null=True)),
                ('nysa_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('rbp_rate', models.DecimalField(blank=True, decimal_places=6, max_digits=7, null=True)),
                ('rbp_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('spta_rate', models.DecimalField(blank=True, decimal_places=6, max_digits=7, null=True)),
                ('spta_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('st_rate', models.DecimalField(blank=True, decimal_places=4, max_digits=5, null=True)),
                ('st_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('toc_total_cost', models.DecimalField(decimal_places=2, max_digits=5)),
                ('real_estate', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='realestate.realestate')),
                ('service_provider', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='realestate.serviceprovider', validators=[realestate.models.electricbilldata.ElectricBillData.validate_service_provider])),
            ],
        ),
        migrations.CreateModel(
            name='DepreciationBillData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_cost', models.DecimalField(decimal_places=2, max_digits=8)),
                ('tax_rel_cost', models.DecimalField(decimal_places=2, max_digits=8)),
                ('notes', models.TextField(blank=True, null=True)),
                ('start_date', models.DateField(validators=[realestate.models.depreciationbilldata.DepreciationBillData.validate_start_date])),
                ('end_date', models.DateField(validators=[realestate.models.depreciationbilldata.DepreciationBillData.validate_end_date])),
                ('paid_date', models.DateField(blank=True, null=True, validators=[realestate.models.depreciationbilldata.DepreciationBillData.validate_paid_date])),
                ('period_usage_pct', models.DecimalField(decimal_places=2, max_digits=5, validators=[realestate.models.depreciationbilldata.DepreciationBillData.validate_pct_usage_0_100])),
                ('real_estate', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='realestate.realestate')),
                ('real_property_value', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='realestate.realpropertyvalue')),
                ('service_provider', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='realestate.serviceprovider', validators=[realestate.models.depreciationbilldata.DepreciationBillData.validate_service_provider])),
            ],
        ),
        migrations.AddConstraint(
            model_name='solarbilldata',
            constraint=models.UniqueConstraint(fields=('real_estate', 'service_provider', 'start_date'), name='unique_realestate_solarbilldata_re_sp_sd'),
        ),
        migrations.AddConstraint(
            model_name='simplebilldata',
            constraint=models.UniqueConstraint(fields=('real_estate', 'service_provider', 'start_date', 'total_cost'), name='unique_realestate_simplebilldata_re_sp_sd_tc'),
        ),
        migrations.AddConstraint(
            model_name='realpropertyvalue',
            constraint=models.UniqueConstraint(fields=('real_estate', 'item', 'purchase_date'), name='unique_re_item_pd'),
        ),
        migrations.AddConstraint(
            model_name='natgasdata',
            constraint=models.UniqueConstraint(fields=('real_estate', 'month_year'), name='unique_realestate_natgasdata_re_my'),
        ),
        migrations.AddConstraint(
            model_name='natgasbilldata',
            constraint=models.UniqueConstraint(fields=('real_estate', 'start_date', 'is_actual'), name='unique_realestate_natgasbilldata_re_sd_ia'),
        ),
        migrations.AddConstraint(
            model_name='natgasbilldata',
            constraint=models.UniqueConstraint(fields=('real_estate', 'end_date', 'is_actual'), name='unique_realestate_natgasbilldata_re_ed_ia'),
        ),
        migrations.AddConstraint(
            model_name='mortgagebilldata',
            constraint=models.UniqueConstraint(fields=('real_estate', 'service_provider', 'start_date'), name='unique_realestate_mortgagebilldata_re_sp_sd'),
        ),
        migrations.AddConstraint(
            model_name='estimatenote',
            constraint=models.UniqueConstraint(fields=('real_estate', 'service_provider', 'note_type'), name='unique_re_sp_nt'),
        ),
        migrations.AddConstraint(
            model_name='electricdata',
            constraint=models.UniqueConstraint(fields=('real_estate', 'month_year'), name='unique_realestate_electricdata_re_my'),
        ),
        migrations.AddConstraint(
            model_name='electricbilldata',
            constraint=models.UniqueConstraint(fields=('real_estate', 'start_date', 'is_actual'), name='unique_realestate_electricbilldata_re_sd_ia'),
        ),
        migrations.AddConstraint(
            model_name='electricbilldata',
            constraint=models.UniqueConstraint(fields=('real_estate', 'end_date', 'is_actual'), name='unique_realestate_electricbilldata_re_ed_ia'),
        ),
        migrations.AddConstraint(
            model_name='depreciationbilldata',
            constraint=models.UniqueConstraint(fields=('real_property_value', 'start_date', 'end_date'), name='unique_realestate_depreciationbilldata_rpv_sd_ed'),
        ),
        migrations.AddConstraint(
            model_name='depreciationbilldata',
            constraint=models.CheckConstraint(check=models.Q(('start_date__iendswith', '-01-01')), name='sd_like_pct-01-01'),
        ),
        migrations.AddConstraint(
            model_name='depreciationbilldata',
            constraint=models.CheckConstraint(check=models.Q(('end_date__iendswith', '-12-31')), name='ed_like_pct-12-31'),
        ),
        migrations.AddConstraint(
            model_name='depreciationbilldata',
            constraint=models.CheckConstraint(check=models.Q(('paid_date__iendswith', '-12-31')), name='pd_like_pct-12-31'),
        ),
        migrations.AddConstraint(
            model_name='depreciationbilldata',
            constraint=models.CheckConstraint(check=models.Q(('period_usage_pct__gte', 0), ('period_usage_pct__lte', 100)), name='pup_between_0_100_inclusive'),
        ),
    ]
