-- =============================================================================
-- schema.sql
-- Supabase (PostgreSQL) schema for the Realty Income Financial Assistant
-- Auto-generated from live Supabase data via export_schema.py
-- Run these statements in the Supabase SQL Editor to recreate the database.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Properties table
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS properties (
    property_id    SERIAL PRIMARY KEY,
    address        VARCHAR NOT NULL,
    metro_area     VARCHAR NOT NULL,
    sq_footage     INTEGER,
    property_type  VARCHAR NOT NULL,
    year_built     INTEGER,
    occupancy_rate NUMERIC,
    created_at     TIMESTAMP DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- Financials table
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS financials (
    financial_id   SERIAL PRIMARY KEY,
    property_id    INTEGER NOT NULL REFERENCES properties(property_id),
    fiscal_year    INTEGER,
    fiscal_quarter INTEGER,
    revenue        NUMERIC,
    net_income     NUMERIC,
    expenses       NUMERIC,
    created_at     TIMESTAMP DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- Seed data: 25 properties
-- -----------------------------------------------------------------------------
INSERT INTO properties (property_id, address, metro_area, sq_footage, property_type, year_built, occupancy_rate) VALUES (1, '1401 W Fulton Market St, Chicago, IL 60607', 'Chicago', 185000, 'Industrial', 2018, 97.50);
INSERT INTO properties (property_id, address, metro_area, sq_footage, property_type, year_built, occupancy_rate) VALUES (2, '8700 W Bryn Mawr Ave, Chicago, IL 60631', 'Chicago', 240000, 'Warehouse', 2015, 100.00);
INSERT INTO properties (property_id, address, metro_area, sq_footage, property_type, year_built, occupancy_rate) VALUES (3, '1000 N Halsted St, Chicago, IL 60642', 'Chicago', 92000, 'Office', 2020, 95.00);
INSERT INTO properties (property_id, address, metro_area, sq_footage, property_type, year_built, occupancy_rate) VALUES (4, '3450 S Racine Ave, Chicago, IL 60608', 'Chicago', 320000, 'Industrial', 2012, 98.00);
INSERT INTO properties (property_id, address, metro_area, sq_footage, property_type, year_built, occupancy_rate) VALUES (5, '200 Park Ave, New York, NY 10166', 'New York', 410000, 'Office', 2008, 91.00);
INSERT INTO properties (property_id, address, metro_area, sq_footage, property_type, year_built, occupancy_rate) VALUES (6, '101 Logistics Blvd, Newark, NJ 07114', 'New York', 550000, 'Warehouse', 2019, 100.00);
INSERT INTO properties (property_id, address, metro_area, sq_footage, property_type, year_built, occupancy_rate) VALUES (7, '45 Industrial Pkwy, Secaucus, NJ 07094', 'New York', 275000, 'Industrial', 2016, 99.00);
INSERT INTO properties (property_id, address, metro_area, sq_footage, property_type, year_built, occupancy_rate) VALUES (8, '333 Hudson St, New York, NY 10013', 'New York', 120000, 'Mixed-Use', 2017, 88.00);
INSERT INTO properties (property_id, address, metro_area, sq_footage, property_type, year_built, occupancy_rate) VALUES (9, '2600 E Vernon Ave, Los Angeles, CA 90058', 'Los Angeles', 310000, 'Industrial', 2014, 98.50);
INSERT INTO properties (property_id, address, metro_area, sq_footage, property_type, year_built, occupancy_rate) VALUES (10, '6200 S Alameda St, Los Angeles, CA 90001', 'Los Angeles', 480000, 'Warehouse', 2021, 100.00);
INSERT INTO properties (property_id, address, metro_area, sq_footage, property_type, year_built, occupancy_rate) VALUES (11, '11100 Santa Monica Blvd, Los Angeles, CA 90025', 'Los Angeles', 78000, 'Office', 2011, 90.00);
INSERT INTO properties (property_id, address, metro_area, sq_footage, property_type, year_built, occupancy_rate) VALUES (12, '3800 W Century Blvd, Inglewood, CA 90303', 'Los Angeles', 195000, 'Industrial', 2018, 97.00);
INSERT INTO properties (property_id, address, metro_area, sq_footage, property_type, year_built, occupancy_rate) VALUES (13, '5555 San Felipe St, Houston, TX 77056', 'Houston', 145000, 'Office', 2013, 86.00);
INSERT INTO properties (property_id, address, metro_area, sq_footage, property_type, year_built, occupancy_rate) VALUES (14, '12000 NW Freeway, Houston, TX 77092', 'Houston', 390000, 'Warehouse', 2017, 100.00);
INSERT INTO properties (property_id, address, metro_area, sq_footage, property_type, year_built, occupancy_rate) VALUES (15, '8900 Tidwell Rd, Houston, TX 77078', 'Houston', 260000, 'Industrial', 2015, 99.00);
INSERT INTO properties (property_id, address, metro_area, sq_footage, property_type, year_built, occupancy_rate) VALUES (16, '2001 Ross Ave, Dallas, TX 75201', 'Dallas', 220000, 'Office', 2019, 93.00);
INSERT INTO properties (property_id, address, metro_area, sq_footage, property_type, year_built, occupancy_rate) VALUES (17, '3100 Innovative Way, Mesquite, TX 75150', 'Dallas', 500000, 'Warehouse', 2020, 100.00);
INSERT INTO properties (property_id, address, metro_area, sq_footage, property_type, year_built, occupancy_rate) VALUES (18, '600 E Hurst Blvd, Hurst, TX 76053', 'Dallas', 175000, 'Industrial', 2016, 96.50);
INSERT INTO properties (property_id, address, metro_area, sq_footage, property_type, year_built, occupancy_rate) VALUES (19, '2355 E Camelback Rd, Phoenix, AZ 85016', 'Phoenix', 98000, 'Office', 2015, 89.00);
INSERT INTO properties (property_id, address, metro_area, sq_footage, property_type, year_built, occupancy_rate) VALUES (20, '4500 W Van Buren St, Phoenix, AZ 85043', 'Phoenix', 420000, 'Industrial', 2022, 100.00);
INSERT INTO properties (property_id, address, metro_area, sq_footage, property_type, year_built, occupancy_rate) VALUES (21, '10000 N 99th Ave, Peoria, AZ 85345', 'Phoenix', 280000, 'Warehouse', 2018, 98.00);
INSERT INTO properties (property_id, address, metro_area, sq_footage, property_type, year_built, occupancy_rate) VALUES (22, '1180 Peachtree St NE, Atlanta, GA 30309', 'Atlanta', 160000, 'Office', 2016, 92.00);
INSERT INTO properties (property_id, address, metro_area, sq_footage, property_type, year_built, occupancy_rate) VALUES (23, '4800 S Atlanta Rd, Smyrna, GA 30080', 'Atlanta', 340000, 'Warehouse', 2019, 100.00);
INSERT INTO properties (property_id, address, metro_area, sq_footage, property_type, year_built, occupancy_rate) VALUES (24, '2200 Sullivan Rd, College Park, GA 30337', 'Atlanta', 225000, 'Industrial', 2014, 97.50);
INSERT INTO properties (property_id, address, metro_area, sq_footage, property_type, year_built, occupancy_rate) VALUES (25, '850 Peachtree Industrial Blvd, Suwanee, GA 30024', 'Atlanta', 65000, 'Data Center', 2021, 95.00);

-- -----------------------------------------------------------------------------
-- Seed data: 100 financial records (4 quarters per property)
-- -----------------------------------------------------------------------------
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (1, 1, 2024, 1, 2850000.00, 855000.00, 1995000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (2, 1, 2024, 2, 2920000.00, 906200.00, 2013800.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (3, 1, 2024, 3, 3010000.00, 963200.00, 2046800.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (4, 1, 2024, 4, 3100000.00, 1023000.00, 2077000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (5, 2, 2024, 1, 3600000.00, 1260000.00, 2340000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (6, 2, 2024, 2, 3720000.00, 1339200.00, 2380800.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (7, 2, 2024, 3, 3800000.00, 1406000.00, 2394000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (8, 2, 2024, 4, 3950000.00, 1501000.00, 2449000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (9, 3, 2024, 1, 1400000.00, 378000.00, 1022000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (10, 3, 2024, 2, 1450000.00, 406000.00, 1044000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (11, 3, 2024, 3, 1480000.00, 429200.00, 1050800.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (12, 3, 2024, 4, 1520000.00, 456000.00, 1064000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (13, 4, 2024, 1, 4800000.00, 1680000.00, 3120000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (14, 4, 2024, 2, 4950000.00, 1782000.00, 3168000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (15, 4, 2024, 3, 5100000.00, 1887000.00, 3213000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (16, 4, 2024, 4, 5250000.00, 1995000.00, 3255000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (17, 5, 2024, 1, 9800000.00, 2450000.00, 7350000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (18, 5, 2024, 2, 10100000.00, 2626000.00, 7474000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (19, 5, 2024, 3, 10250000.00, 2767500.00, 7482500.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (20, 5, 2024, 4, 10500000.00, 2940000.00, 7560000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (21, 6, 2024, 1, 8200000.00, 3116000.00, 5084000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (22, 6, 2024, 2, 8450000.00, 3295500.00, 5154500.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (23, 6, 2024, 3, 8700000.00, 3480000.00, 5220000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (24, 6, 2024, 4, 9000000.00, 3690000.00, 5310000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (25, 7, 2024, 1, 4125000.00, 1485000.00, 2640000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (26, 7, 2024, 2, 4250000.00, 1572500.00, 2677500.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (27, 7, 2024, 3, 4400000.00, 1672000.00, 2728000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (28, 7, 2024, 4, 4550000.00, 1774500.00, 2775500.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (29, 8, 2024, 1, 2400000.00, 600000.00, 1800000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (30, 8, 2024, 2, 2500000.00, 650000.00, 1850000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (31, 8, 2024, 3, 2580000.00, 696600.00, 1883400.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (32, 8, 2024, 4, 2650000.00, 742000.00, 1908000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (33, 9, 2024, 1, 4650000.00, 1720500.00, 2929500.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (34, 9, 2024, 2, 4800000.00, 1824000.00, 2976000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (35, 9, 2024, 3, 4950000.00, 1930500.00, 3019500.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (36, 9, 2024, 4, 5100000.00, 2040000.00, 3060000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (37, 10, 2024, 1, 7200000.00, 2880000.00, 4320000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (38, 10, 2024, 2, 7450000.00, 3054500.00, 4395500.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (39, 10, 2024, 3, 7700000.00, 3234000.00, 4466000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (40, 10, 2024, 4, 8000000.00, 3440000.00, 4560000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (41, 11, 2024, 1, 1170000.00, 304200.00, 865800.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (42, 11, 2024, 2, 1200000.00, 324000.00, 876000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (43, 11, 2024, 3, 1230000.00, 344400.00, 885600.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (44, 11, 2024, 4, 1260000.00, 365400.00, 894600.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (45, 12, 2024, 1, 2925000.00, 1023750.00, 1901250.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (46, 12, 2024, 2, 3000000.00, 1080000.00, 1920000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (47, 12, 2024, 3, 3100000.00, 1147000.00, 1953000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (48, 12, 2024, 4, 3200000.00, 1216000.00, 1984000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (49, 13, 2024, 1, 1740000.00, 417600.00, 1322400.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (50, 13, 2024, 2, 1800000.00, 450000.00, 1350000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (51, 13, 2024, 3, 1850000.00, 481000.00, 1369000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (52, 13, 2024, 4, 1900000.00, 513000.00, 1387000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (53, 14, 2024, 1, 5850000.00, 2281500.00, 3568500.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (54, 14, 2024, 2, 6000000.00, 2400000.00, 3600000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (55, 14, 2024, 3, 6200000.00, 2542000.00, 3658000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (56, 14, 2024, 4, 6400000.00, 2688000.00, 3712000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (57, 15, 2024, 1, 3900000.00, 1443000.00, 2457000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (58, 15, 2024, 2, 4050000.00, 1539000.00, 2511000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (59, 15, 2024, 3, 4200000.00, 1638000.00, 2562000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (60, 15, 2024, 4, 4350000.00, 1740000.00, 2610000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (61, 16, 2024, 1, 3300000.00, 858000.00, 2442000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (62, 16, 2024, 2, 3400000.00, 918000.00, 2482000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (63, 16, 2024, 3, 3500000.00, 980000.00, 2520000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (64, 16, 2024, 4, 3600000.00, 1044000.00, 2556000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (65, 17, 2024, 1, 7500000.00, 3000000.00, 4500000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (66, 17, 2024, 2, 7750000.00, 3177500.00, 4572500.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (67, 17, 2024, 3, 8000000.00, 3360000.00, 4640000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (68, 17, 2024, 4, 8250000.00, 3547500.00, 4702500.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (69, 18, 2024, 1, 2625000.00, 945000.00, 1680000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (70, 18, 2024, 2, 2700000.00, 1002600.00, 1697400.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (71, 18, 2024, 3, 2800000.00, 1064000.00, 1736000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (72, 18, 2024, 4, 2900000.00, 1131000.00, 1769000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (73, 19, 2024, 1, 1176000.00, 282240.00, 893760.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (74, 19, 2024, 2, 1220000.00, 305000.00, 915000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (75, 19, 2024, 3, 1260000.00, 327600.00, 932400.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (76, 19, 2024, 4, 1300000.00, 351000.00, 949000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (77, 20, 2024, 1, 6300000.00, 2457000.00, 3843000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (78, 20, 2024, 2, 6500000.00, 2600000.00, 3900000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (79, 20, 2024, 3, 6750000.00, 2768000.00, 3982000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (80, 20, 2024, 4, 7000000.00, 2940000.00, 4060000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (81, 21, 2024, 1, 4200000.00, 1638000.00, 2562000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (82, 21, 2024, 2, 4350000.00, 1740000.00, 2610000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (83, 21, 2024, 3, 4500000.00, 1845000.00, 2655000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (84, 21, 2024, 4, 4650000.00, 1953000.00, 2697000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (85, 22, 2024, 1, 2400000.00, 624000.00, 1776000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (86, 22, 2024, 2, 2480000.00, 669600.00, 1810400.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (87, 22, 2024, 3, 2550000.00, 714000.00, 1836000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (88, 22, 2024, 4, 2620000.00, 759800.00, 1860200.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (89, 23, 2024, 1, 5100000.00, 1989000.00, 3111000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (90, 23, 2024, 2, 5300000.00, 2120000.00, 3180000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (91, 23, 2024, 3, 5500000.00, 2255000.00, 3245000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (92, 23, 2024, 4, 5700000.00, 2394000.00, 3306000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (93, 24, 2024, 1, 3375000.00, 1215000.00, 2160000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (94, 24, 2024, 2, 3500000.00, 1295000.00, 2205000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (95, 24, 2024, 3, 3600000.00, 1368000.00, 2232000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (96, 24, 2024, 4, 3750000.00, 1462500.00, 2287500.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (97, 25, 2024, 1, 1950000.00, 799500.00, 1150500.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (98, 25, 2024, 2, 2050000.00, 861000.00, 1189000.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (99, 25, 2024, 3, 2150000.00, 924500.00, 1225500.00);
INSERT INTO financials (financial_id, property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES (100, 25, 2024, 4, 2250000.00, 990000.00, 1260000.00);
