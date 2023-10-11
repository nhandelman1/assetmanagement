use am_dev;
show tables;
SET foreign_key_checks = 0;
SET foreign_key_checks = 1;



# Notes for creating new meta table (e.g. stocks)
# must be same name as data_subtypes prefix (e.g. stocks, etfs)

# Notes for creating new time series table (e.g. stocks_price_1D)
# use format prefix_midfix_freq
# prefix must be same name as data_subtypes prefix (e.g. stocks, etfs)
# midfix must be same as data_types midfix (e.g. _price)
# postfix must be same as data_freq freq (e.g. , 5M)
# 1st column is the id int primary key
# 2nd column is the db_table_meta_id (e.g. securities_id)
#	db_table_meta is described below (it is a column in data_types table)
# 3rd column is a date or date_time column named 'date_time'

# db_table_meta is the full name of the meta table associated with the data type
#	e.g. securities table for Security data type
#	can be duplicated. A possible "Security Returns" data type would also
#		have the securities table as the meta table
# db_data_table_midfix is midfix value for any data table associated with 
#	the data type. e.g. stocks_price_1D (midfix value is price)
create table data_types (
	id smallint not null auto_increment primary key,
    name varchar(100) not null,
    db_table_meta varchar(100) not null,
    db_data_table_midfix varchar(100) not null,
    unique key unique_name (name)
);

select * from etfs_price_1D;

# db_data_table_meta is the full name of the meta table associated with the data subtype
#	e.g. stocks table for stocks data subtype
# db_data_table_prefix is prefix value for any data table associated with 
#	the data subtype. e.g. stocks_price_1D (prefix value is stocks)
create table data_subtypes (
	id smallint not null auto_increment primary key, 
    name varchar(100) not null, 
    type_id smallint not null,
    db_table_meta varchar(100) not null,
    db_data_table_prefix varchar(100) not null,
	unique key unique_name (name),
    foreign key (type_id) references data_types (id));

# Format: countfreq_type
#	count: 1,2,3,4,5,...
#	freq_type: S (second), M (minute), H (hour), D (day), Mo(Month), Y (year)
# e.g. 1S, 5M, 10D
# String sort with this format wont be clear but already have tables named
# format_str: up to "yyyy-MM-dd hh:mm:ss"
create table data_freq (
	id tinyint not null auto_increment primary key,
	freq varchar(5) not null,
    format_str varchar(20),
    unique key unique_freq (freq)
);

# this table has to be refactored out
create table price_freq (
	id tinyint not null auto_increment primary key,
	freq varchar(5) not null
);

# for each record in this table, there must be a table with the name format
#	'db_data_table_prefix'_'db_data_table_midfix'_'freq'
# 'db_data_table_prefix' is associated with the subtype_id for the record
# 'freq' is associated with the freq_id for the record
# 'db_data_table_midfix' is associated with the data type associated with 
#	the subtype_id
create table data_subtype_freq (
	id smallint not null auto_increment primary key,
    subtype_id smallint not null,
    freq_id tinyint not null,
    foreign key (subtype_id) references data_subtypes (id),
    foreign key (freq_id) references data_freq (id)
);

create table data_source (
	id smallint not null auto_increment primary key,
    name varchar(100) not null,
    notes text,
    unique key unique_name (name));

create table sector (
	id smallint not null auto_increment primary key,
    name varchar (100) not null, 
    notes text,
	unique key unique_name (name));

create table industry (
	id smallint not null auto_increment primary key,
    name varchar (100) not null,
    sector_id smallint, 
    notes text,
    unique key unique_name (name),
    foreign key (sector_id) references sector (id));

create table company (
	id smallint not null auto_increment primary key,
    name varchar (100) not null,
    notes text,
    unique key unique_name (name));

create table company_industry (
	id mediumint not null auto_increment primary key,
    company_id smallint not null,
    industry_id smallint not null,
    constraint cid_iid unique (company_id, industry_id),
    foreign key (company_id) references company (id),
    foreign key (industry_id) references industry (id));

create table region (
	id smallint not null auto_increment primary key,
    name varchar(100) not null,
    notes text,
    unique key unique_name (name));

create table country (
	id smallint not null auto_increment primary key,
    name varchar(100) not null,
    notes text,
    unique key unique_name (name));

create table region_country (
	id smallint not null auto_increment primary key,
    region_id smallint not null,
    country_id smallint not null,
    constraint rid_cid unique (region_id, country_id),
    foreign key (region_id) references region (id),
    foreign key (country_id) references country (id));

create table securities (
	id int not null auto_increment primary key,
    ticker varchar(20) not null, 
    type_id smallint not null,
    unique key unique_ticker (ticker),
    foreign key (type_id) references data_subtypes (id));

create table sec_sec (
	id bigint not null auto_increment primary key,
    sec_id int not null,
    sec_under_id int not null,
    weight decimal(5,2),
    constraint sid_sid unique (sec_id, sec_under_id),
    foreign key (sec_id) references securities (id),
    foreign key (sec_under_id) references securities (id));

create table stocks (
	id mediumint not null auto_increment primary key, 
    securities_id int not null, 
    company_id smallint,
    unique key unique_securities_id (securities_id),
    foreign key (securities_id) references securities (id),
    foreign key (company_id) references company (id));

create table etf_asset_class (
	id tinyint not null auto_increment primary key,
    name varchar(50) not null,    
    notes text,
    unique key unique_name (name));

create table etf_categories (
	id smallint not null auto_increment primary key,
    name varchar(100) not null,
    notes text,
    unique key unique_name (name));

create table etf_asset_class_size (
	id tinyint not null auto_increment primary key,
    name varchar(20) not null,
    notes text,
    unique key unique_name (name));

create table etf_asset_class_style (
	id tinyint not null auto_increment primary key,
    name varchar(20) not null,
    notes text,
    unique key unique_name (name));

create table etf_bond_type (
	id tinyint not null auto_increment primary key,
    name varchar(50) not null,
    notes text,
    unique key unique_name (name));

create table etf_bond_duration_type (
	id tinyint not null auto_increment primary key,
    name varchar(20) not null,
    notes text,
    unique key unique_name (name));

create table etf_commodity_type (
	id tinyint not null auto_increment primary key,
    name varchar(20) not null,
    notes text,
    unique key unique_name (name));
    
create table etf_commodity (
	id tinyint not null auto_increment primary key,
    name varchar(20) not null,
    notes text,
    unique key unique_name (name));

create table etf_commodity_exposure_type (
	id tinyint not null auto_increment primary key,
    name varchar(50) not null,
    notes text,
    unique key unique_name (name));
    
create table etf_currency_type (
	id tinyint not null auto_increment primary key,
    name varchar(20) not null,
    notes text,
    unique key unique_name (name));    

create table etfs (
	id mediumint not null auto_increment primary key, 
    securities_id int not null,
    name varchar(100),
    asset_class_id tinyint not null,
    issue_company_id smallint,
    index_id smallint,
    lev tinyint,
    fee decimal(3,2),
    inception datetime,
    category_id smallint,
    region_country_id smallint,
    industry_id smallint,
    asset_class_size_id tinyint,
    asset_class_style_id tinyint,
    bond_type_id tinyint,
    bond_duration_type_id tinyint,
    commodity_type_id tinyint,
    commodity_id tinyint,
    commodity_exposure_type_id tinyint,
    currency_type_id tinyint,
    unique key unique_id (id),
    foreign key (securities_id) references securities (id),
    foreign key (asset_class_id) references etf_asset_class (id),
    foreign key (index_id) references indices (id),
    foreign key (category_id) references etf_categories (id),
    foreign key (issue_company_id) references company (id),
    foreign key (region_country_id) references region_country (id),
    foreign key (industry_id) references industry (id),
    foreign key (asset_class_size_id) references etf_asset_class_size (id),
    foreign key (asset_class_style_id) references etf_asset_class_style (id),
    foreign key (bond_type_id) references etf_bond_type (id),
    foreign key (bond_duration_type_id) references etf_bond_duration_type (id),
    foreign key (commodity_type_id) references etf_commodity_type (id),
    foreign key (commodity_id) references etf_commodity (id),
    foreign key (commodity_exposure_type_id) references etf_commodity_exposure_type (id),
    foreign key (currency_type_id) references etf_currency_type (id));

create table indices (
	id smallint not null auto_increment primary key, 
    securities_id int not null, 
    name varchar(100),
    issue_company_id smallint,
    unique key unique_securities_id (securities_id),
    foreign key (securities_id) references securities (id),
    foreign key (issue_company_id) references company (id));

create table options_cp (
	id tinyint not null auto_increment primary key,
    cp varchar(4),
    unique key unique_cp (cp));

create table options_types (
	id smallint not null auto_increment primary key,
    name varchar(100) not null,
    unique key unique_name (name));

create table options (
	id mediumint not null auto_increment primary key,
    securities_id int not null,
    issued datetime,
    expiry datetime not null,
    strike decimal(8,2) not null,
    cp_id tinyint not null,
    type_id smallint not null,
    unique key unique_securities_id (securities_id),
    foreign key (securities_id) references securities (id),
    foreign key (cp_id) references options_cp (id),
    foreign key (type_id) references options_types (id));

create table stocks_price_1D (
	id int not null auto_increment primary key,
    securities_id int not null,
    date_time date not null,
    open decimal(9,2),
    high decimal(9,2),
    low decimal(9,2),
    close decimal(9,2),
    adj_close decimal(9,2),
    volume bigint,
    constraint sid_dt unique (securities_id, date_time),
    foreign key (securities_id) references securities (id));

create table stocks_price_5M (
	id bigint not null auto_increment primary key,
    securities_id int not null,
    date_time datetime not null,
    open decimal(9,2),
    high decimal(9,2),
    low decimal(9,2),
    close decimal(9,2),
    adj_close decimal(9,2),
    volume bigint,
    constraint sid_dt unique (securities_id, date_time),
    foreign key (securities_id) references securities (id));
    
create table etfs_price_1D (
	id int not null auto_increment primary key,
    securities_id int not null,
    date_time date not null,
    open decimal(9,2),
    high decimal(9,2),
    low decimal(9,2),
    close decimal(9,2),
    adj_close decimal(9,2),
    volume bigint,
    constraint sid_dt unique (securities_id, date_time),
    foreign key (securities_id) references securities (id));
    
create table etfs_price_5M (
	id bigint not null auto_increment primary key,
    securities_id int not null,
    date_time datetime not null,
    open decimal(9,2),
    high decimal(9,2),
    low decimal(9,2),
    close decimal(9,2),
    adj_close decimal(9,2),
    volume bigint,
    constraint sid_dt unique (securities_id, date_time),
    foreign key (securities_id) references securities (id));

create table indices_price_1D (
	id int not null auto_increment primary key,
    securities_id int not null,
    date_time date not null,
    open decimal(9,2),
    high decimal(9,2),
    low decimal(9,2),
    close decimal(9,2),
    adj_close decimal(9,2),
    constraint sid_dt unique (securities_id, date_time),
    foreign key (securities_id) references securities (id));

create table indices_price_5M (
	id bigint not null auto_increment primary key,
	securities_id int not null,
    date_time datetime not null,
    open decimal(9,2),
    high decimal(9,2),
    low decimal(9,2),
    close decimal(9,2),
    adj_close decimal(9,2),
    constraint sid_dt unique (securities_id, date_time),
    foreign key (securities_id) references securities (id));

create table se_market_data (
	id int not null auto_increment primary key,
    securities_id int not null,
    date_time date not null,
    dividend decimal(5,2),
    splits decimal(6,3),
    shares_float bigint,
    shares_short bigint,
    shares_outstanding bigint,
    aum bigint,
    constraint sid_date unique (securities_id, date_time),
    foreign key (securities_id) references securities (id));
    
create table iex_api_tokens(
	id tinyint not null auto_increment primary key,
    token varchar(100),
    type enum("Secret", "Publishable"),
    env enum("Production", "Sandbox"));

create table real_estate (
	id smallint not null auto_increment primary key,
    address varchar(70) not null unique,
    street_num varchar(10) not null,
    street_name varchar(20) not null,
    apt varchar(10),
    city varchar(20) not null,
    state char(2) not null,
    zip_code char(5) not null,
    bill_tax_related boolean not null
);

create table service_provider (
	id smallint not null auto_increment primary key,
    provider varchar(100) not null unique,
	tax_category enum('CleaningMaintenance', 'Depreciation', 'Income', 'Insurance', 'MortgageInterest', 'None', 'Repairs', 'Supplies', 'Taxes', 'Utilities') not null
);

#alter table real_property_values modify dep_class enum('None-None-None-None', 'GDS-RRP-SL-MM', 'GDS-YEAR5-SL-MM') not null;
create table real_property_values (
	id smallint not null auto_increment primary key,
    real_estate_id smallint not null,
    item varchar(100) not null,
    purchase_date date not null,
    disposal_date date,
    cost_basis decimal(11, 2) not null,
    dep_class enum('None-None-None-None', 'GDS-RRP-SL-MM', 'GDS-YEAR5-SL-MM') not null,
    notes text,
    unique key unique_reid_item_purchasedate (real_estate_id, item, purchase_date),
    foreign key (real_estate_id) references real_estate (id)
);

create table mysunpower_hourly_data (
	dt datetime not null primary key,
    solar_kwh decimal(5,2),
    home_kwh decimal(5,2)
);

create table solar_bill_data (
	id int not null auto_increment primary key,
    real_estate_id smallint not null,
    service_provider_id smallint not null,
	start_date date not null,
    end_date date not null,
    solar_kwh smallint unsigned not null,
    home_kwh smallint unsigned not null,
    total_cost decimal(8,2) not null,
    tax_rel_cost decimal(8,2) not null,
    actual_costs decimal(8,2) not null,
    oc_bom_basis decimal(8,2) not null,
    oc_pnl_pct decimal(4,2) not null,
    oc_pnl decimal(8,2) not null,
    oc_eom_basis decimal(8,2) not null,
    paid_date date,
    notes text,
    unique key unique_reid_spid_startdate (real_estate_id, service_provider_id, start_date),
    foreign key (real_estate_id) references real_estate (id),
    foreign key (service_provider_id) references service_provider (id)
);

create table electric_bill_data (
	id smallint not null auto_increment primary key, 
    real_estate_id smallint not null,
    service_provider_id smallint not null,
    start_date date not null,
    end_date date not null,
    total_kwh smallint unsigned not null,
    eh_kwh smallint unsigned not null,
    bank_kwh mediumint unsigned not null,
    total_cost decimal(6,2) not null,
    tax_rel_cost decimal(8,2) not null,
    bs_rate decimal(4,2) not null,
    bs_cost decimal(6,2) not null,
    first_kwh smallint unsigned,
    first_rate decimal(5,4),
    first_cost decimal(6,2),
    next_kwh smallint unsigned,
    next_rate decimal(5,4),
    next_cost decimal(6,2),
    cbc_rate decimal(5,4),
    cbc_cost decimal(4,2),
    mfc_rate decimal(7,6),
    mfc_cost decimal(4,2),
    dsc_total_cost decimal(6,2) not null,
    psc_rate decimal(7,6),
    psc_cost decimal(6,2),
    psc_total_cost decimal(6,2),
    der_rate decimal(7,6),
    der_cost decimal(4,2),
    dsa_rate decimal(7,6),
    dsa_cost decimal(4,2),
    rda_rate decimal(7,6),
    rda_cost decimal(4,2),
    nysa_rate decimal(7,6),
    nysa_cost decimal(4,2),
    rbp_rate decimal(7,6),
    rbp_cost decimal(4,2),
    spta_rate decimal(7,6),
    spta_cost decimal(4,2),
    st_rate decimal(5,4),
    st_cost decimal(4,2),
    toc_total_cost decimal(5,2) not null,
    is_actual boolean not null,
    paid_date date,
    notes text,
    unique key unique_reid_start_date_actual (real_estate_id, start_date, is_actual),
    unique key unique_reid_end_date_actual (real_estate_id, end_date, is_actual),
    foreign key (real_estate_id) references real_estate (id),
    foreign key (service_provider_id) references service_provider (id)
);

create table electric_data (
	id smallint not null auto_increment primary key,
    real_estate_id smallint not null,
	service_provider_id smallint not null,
    month_date date not null,
    month_year char(6) not null,
    first_kwh smallint unsigned not null,
    first_rate decimal(5,4) not null,
    next_rate decimal(5,4) not null,
    mfc_rate decimal(7,6),
    psc_rate decimal(7,6),
    der_rate decimal(7,6),
    dsa_rate decimal(7,6),
    rda_rate decimal(7,6),
    nysa_rate decimal(7,6),
    rbp_rate decimal(7,6),
    spta_rate decimal(7,6),
    unique key unique_reid_month_year (real_estate_id, month_year),
    foreign key (real_estate_id) references real_estate (id),
    foreign key (service_provider_id) references service_provider (id)
);

create table estimate_notes (
	id smallint not null auto_increment primary key,
    real_estate_id smallint not null,
    service_provider_id smallint not null,
    note_type varchar(20) not null,
    note text not null,
    note_order smallint not null,
    unique key unique_reid_spid_notetype (real_estate_id, service_provider_id, note_type),
    foreign key (real_estate_id) references real_estate (id),
    foreign key (service_provider_id) references service_provider(id)
);

create table natgas_bill_data (
	id smallint not null auto_increment primary key, 
    real_estate_id smallint not null,
    service_provider_id smallint not null,
    start_date date not null,
    end_date date not null,
    total_therms smallint unsigned not null,
    saved_therms smallint unsigned not null,
    total_cost decimal(6,2) not null,
    tax_rel_cost decimal(8,2) not null,
    bsc_therms decimal(3,1) not null,
    bsc_cost decimal(5,2) not null,
    next_therms decimal(4,1) not null,
    next_rate decimal(5,4) not null,
    next_cost decimal(5,2) not null,
    over_therms decimal(4,1),
    over_rate decimal(5,4),
    over_cost decimal(5,2),
    dra_rate decimal(7,6),
    dra_cost decimal(4,2),
    sbc_rate decimal(7,6),
    sbc_cost decimal(4,2),
    tac_rate decimal(7,6),
    tac_cost decimal(4,2),
    bc_cost decimal(4,2),
    ds_nysls_rate decimal(7,6),
    ds_nysls_cost decimal(4,2),
    ds_nysst_rate decimal(5,4),
    ds_nysst_cost decimal(4,2),
    ds_total_cost decimal(6,2) not null,
    gs_rate decimal(7,6) not null,
    gs_cost decimal(6,2) not null,
    ss_nysls_rate decimal(7,6),
    ss_nysls_cost decimal(4,2),
    ss_nysst_rate decimal(5,4),
    ss_nysst_cost decimal(4,2),
    ss_total_cost decimal(6,2) not null,
    pbc_cost decimal(4,2),
    oca_total_cost decimal(5,2) not null,
    is_actual boolean not null,
    paid_date date,
    notes text,
    unique key unique_reid_start_date_actual (real_estate_id, start_date, is_actual),
    unique key unique_reid_end_date_actual (real_estate_id, end_date, is_actual),
    foreign key (real_estate_id) references real_estate (id),
    foreign key (service_provider_id) references service_provider(id)
);

create table natgas_data (
	id smallint not null auto_increment primary key,
    real_estate_id smallint not null,
    service_provider_id smallint not null,
    month_date date not null,
    month_year char(6) not null,
    bsc_therms decimal(3,1) not null,
    bsc_rate decimal(6,4) not null,
    next_therms decimal(4,1) not null,
    next_rate decimal(5,4) not null,
    over_rate decimal(5,4) not null,
    dra_rate decimal(7,6),
    wna_low_rate decimal(7,6),
	wna_high_rate decimal(7,6),
    sbc_rate decimal(7,6),
    tac_rate decimal(7,6),
    bc_rate decimal(4,2),
    ds_nysls_rate decimal(7,6),
    ds_nysst_rate decimal(5,4),
    gs_rate decimal(7,6) not null,
    ss_nysls_rate decimal(7,6),
    ss_nysst_rate decimal(5,4),
    pbc_rate decimal(4,2),
    unique key unique_reid_month_year (real_estate_id, month_year),
    foreign key (real_estate_id) references real_estate (id),
    foreign key (service_provider_id) references service_provider(id)
);

create table simple_bill_data (
	id int not null auto_increment primary key,
    real_estate_id smallint not null,
    service_provider_id smallint not null,
	start_date date not null,
    end_date date not null,
    total_cost decimal(6,2) not null,
    tax_rel_cost decimal(8,2) not null,
    paid_date date,
    notes text,
    # not likely that this constraint will be violated for a legitimate reason
    unique key unique_reid_spid_startdate_totalcost (real_estate_id, service_provider_id, start_date, total_cost),
    foreign key (real_estate_id) references real_estate (id),
    foreign key (service_provider_id) references service_provider(id)
);

create table mortgage_bill_data (
	id int not null auto_increment primary key,
    real_estate_id smallint not null,
    service_provider_id smallint not null,
	start_date date not null,
    end_date date not null,
    total_cost decimal(8,2) not null,
    tax_rel_cost decimal(8,2) not null,
    outs_prin decimal (10, 2) not null,
    esc_bal decimal (8,2) not null,
    prin_pmt decimal (7,2) not null,
    int_pmt decimal (7,2) not null,
    esc_pmt decimal (7,2) not null,
    other_pmt decimal (7,2) not null,
    paid_date date,
    notes text,
    unique key unique_reid_spid_startdate (real_estate_id, service_provider_id, start_date),
    foreign key (real_estate_id) references real_estate (id),
    foreign key (service_provider_id) references service_provider(id)
);

# depreciation bills are yearly bills per item (real_property_values)
# paid_date can be any date in the year (choose to use 12-31)
create table depreciation_bill_data (
	id int not null auto_increment primary key,
    real_estate_id smallint not null,
    service_provider_id smallint not null,
    real_property_values_id smallint not null,
	start_date date not null check (start_date like "%-01-01"),
    end_date date not null check (end_date like "%-12-31"),
    # "period" instead of "year" due to purchase date or disposal date probably aren't on Jan 1st
    period_usage_pct decimal(5,2) not null check (period_usage_pct>=000.00 and period_usage_pct <= 100.00),
    total_cost decimal(8,2) not null,
    tax_rel_cost decimal(8,2) not null,
    paid_date date check (paid_date like "%-12-31"),
    notes text,
    # one depreciation bill per depreciation item per year
    unique key unique_rpvid_startdate_enddate (real_property_values_id, start_date, end_date),
    foreign key (real_estate_id) references real_estate (id),
    foreign key (service_provider_id) references service_provider(id),
    foreign key (real_property_values_id) references real_property_values(id)
);
