-- =============================================================================
-- schema.sql
-- Supabase (PostgreSQL) schema for the Realty Income Financial Assistant
-- Run these statements in the Supabase SQL Editor to recreate the database.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Properties table
-- Stores physical property records for Realty Income Corporation locations.
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
-- Stores quarterly financial performance data at the individual property level.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS financials (
    financial_id  SERIAL PRIMARY KEY,
    property_id   INTEGER NOT NULL REFERENCES properties(property_id),
    fiscal_year   INTEGER,
    fiscal_quarter INTEGER,
    revenue       NUMERIC,
    net_income    NUMERIC,
    expenses      NUMERIC,
    created_at    TIMESTAMP DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- Sample data — 20 properties across major US metro areas
-- -----------------------------------------------------------------------------
INSERT INTO properties (address, metro_area, sq_footage, property_type, year_built, occupancy_rate) VALUES
    ('1201 N LaSalle Dr, Chicago, IL',        'Chicago',       4500,  'retail',     1998, 0.96),
    ('875 W Madison St, Chicago, IL',          'Chicago',       6200,  'industrial', 2005, 0.99),
    ('400 W Erie St, Chicago, IL',             'Chicago',       3100,  'office',     2001, 0.91),
    ('2340 Commerce St, Dallas, TX',           'Dallas',        5800,  'retail',     2003, 0.97),
    ('1100 Elm St, Dallas, TX',                'Dallas',        7400,  'industrial', 2008, 1.00),
    ('500 Commerce St, Dallas, TX',            'Dallas',        2900,  'office',     1999, 0.88),
    ('180 Peachtree St NE, Atlanta, GA',       'Atlanta',       4100,  'retail',     2002, 0.95),
    ('1000 Abernathy Rd, Atlanta, GA',         'Atlanta',       6800,  'industrial', 2007, 0.98),
    ('3500 Lenox Rd NE, Atlanta, GA',          'Atlanta',       3700,  'office',     2004, 0.90),
    ('400 Park Ave, New York, NY',             'New York',      8200,  'retail',     1995, 0.99),
    ('10 W 33rd St, New York, NY',             'New York',      9500,  'office',     2000, 0.93),
    ('6550 Hollywood Blvd, Los Angeles, CA',   'Los Angeles',   5100,  'retail',     2006, 0.96),
    ('2000 E Imperial Hwy, Los Angeles, CA',   'Los Angeles',   7900,  'industrial', 2010, 1.00),
    ('1888 Century Park E, Los Angeles, CA',   'Los Angeles',   4400,  'office',     2003, 0.89),
    ('4800 Main St, Kansas City, MO',          'Kansas City',   3900,  'retail',     2001, 0.94),
    ('7000 E 12th St, Kansas City, MO',        'Kansas City',   6100,  'industrial', 2009, 0.99),
    ('1 Convention Plaza, St. Louis, MO',      'St. Louis',     4700,  'retail',     1997, 0.92),
    ('800 Market St, Philadelphia, PA',        'Philadelphia',  5300,  'retail',     2002, 0.97),
    ('1500 Market St, Philadelphia, PA',       'Philadelphia',  6600,  'office',     2005, 0.91),
    ('200 Galleria Pkwy, Atlanta, GA',         'Atlanta',       4900,  'retail',     2000, 0.95);

-- -----------------------------------------------------------------------------
-- Sample financial records — one row per property (fiscal_year 2024, Q4)
-- -----------------------------------------------------------------------------
INSERT INTO financials (property_id, fiscal_year, fiscal_quarter, revenue, net_income, expenses) VALUES
    (1,  2024, 4, 980000,  420000,  560000),
    (2,  2024, 4, 1450000, 680000,  770000),
    (3,  2024, 4, 720000,  290000,  430000),
    (4,  2024, 4, 1100000, 510000,  590000),
    (5,  2024, 4, 1620000, 740000,  880000),
    (6,  2024, 4, 640000,  255000,  385000),
    (7,  2024, 4, 890000,  390000,  500000),
    (8,  2024, 4, 1530000, 710000,  820000),
    (9,  2024, 4, 810000,  345000,  465000),
    (10, 2024, 4, 2100000, 990000,  1110000),
    (11, 2024, 4, 1880000, 850000,  1030000),
    (12, 2024, 4, 1150000, 530000,  620000),
    (13, 2024, 4, 1740000, 790000,  950000),
    (14, 2024, 4, 960000,  415000,  545000),
    (15, 2024, 4, 870000,  375000,  495000),
    (16, 2024, 4, 1350000, 620000,  730000),
    (17, 2024, 4, 1040000, 470000,  570000),
    (18, 2024, 4, 1180000, 545000,  635000),
    (19, 2024, 4, 1490000, 680000,  810000),
    (20, 2024, 4, 920000,  400000,  520000);
