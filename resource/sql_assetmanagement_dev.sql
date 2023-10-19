use assetmanagement_dev;
show tables;
SELECT @@sql_mode;
SET SQL_SAFE_UPDATES = 1;
SET FOREIGN_KEY_CHECKS = 1;

select * from realestate_natgasdata;
select * from realestate_natgasbilldata where real_estate_id = 1 order by start_date desc;
select * from realestate_electricbilldata order by start_date desc;
select * from realestate_electricdata;
select * from realestate_solarbilldata;
select * from realestate_depreciationbilldata;
select id, end_date, real_estate_id, total_cost, notes, bill_file from realestate_electricbilldata where is_actual=True;
select * from realestate_electricdata;
select * from realestate_estimatenote;
select * from realestate_mortgagebilldata order by start_date desc;
select * from realestate_mysunpowerhourlydata;
select id, end_date, real_estate_id, total_cost, notes, bill_file  from realestate_natgasbilldata where is_actual=True;
select * from realestate_natgasdata;
select * from realestate_realestate;
select * from realestate_realpropertyvalue;
select * from realestate_serviceprovider;
select * from realestate_simplebilldata where service_provider_id = 27 and real_estate_id = 2 order by start_date desc;


use am_dev;
select count(*), sum(solar_kwh), sum(home_kwh) from mysunpower_hourly_data where dt >= "2023-07-16 00:00:00" and dt <= "2023-08-16 23:59:59";
select * from estimate_notes;
select * from real_property_values;
select * from mysunpower_hourly_data order by dt;
select * from electric_bill_data;# order by real_estate_id, service_provider_id, start_date;
select * from electric_data;
select * from estimate_notes order by service_provider_id, note_order;
select * from natgas_bill_data;# order by real_estate_id, service_provider_id, start_date;
select * from natgas_data;
select * from simple_bill_data;# order by real_estate_id, service_provider_id, start_date;
select * from solar_bill_data;
select * from mortgage_bill_data;# order by real_estate_id, service_provider_id, start_date;
select * from depreciation_bill_data;

insert into estimate_notes (real_estate_id, provider, note_type, note, note_order) values 
(1, 'NationalGrid', 'wna_low_rate', 
'https://www.nationalgridus.com/Long-Island-NY-Home/Bills-Meters-and-Rates/Weather-Normalization-Adjustment -> From Date and To Date matching bill dates -> SC1B column 4-50 therms (or lowest therm level).
 WNA is added to previously entered DRA to get final DRA.', 
1);