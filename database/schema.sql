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
    property_id   SERIAL PRIMARY KEY,
    address       TEXT NOT NULL,
    metro_area    TEXT NOT NULL,
    sq_footage    INTEGER,
    property_type TEXT NOT NULL
);

-- -----------------------------------------------------------------------------
-- Financials table
-- Stores annual financial performance data at the individual property level.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS financials (
    id          SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL REFERENCES properties(property_id),
    revenue     NUMERIC(15, 2),
    net_income  NUMERIC(15, 2),
    expenses    NUMERIC(15, 2)
);

-- -----------------------------------------------------------------------------
-- Sample data — 20 properties across major US metro areas
-- -----------------------------------------------------------------------------
INSERT INTO properties (address, metro_area, sq_footage, property_type) VALUES
    ('1201 N LaSalle Dr, Chicago, IL',        'Chicago',       4500,  'retail'),
    ('875 W Madison St, Chicago, IL',          'Chicago',       6200,  'industrial'),
    ('400 W Erie St, Chicago, IL',             'Chicago',       3100,  'office'),
    ('2340 Commerce St, Dallas, TX',           'Dallas',        5800,  'retail'),
    ('1100 Elm St, Dallas, TX',                'Dallas',        7400,  'industrial'),
    ('500 Commerce St, Dallas, TX',            'Dallas',        2900,  'office'),
    ('180 Peachtree St NE, Atlanta, GA',       'Atlanta',       4100,  'retail'),
    ('1000 Abernathy Rd, Atlanta, GA',         'Atlanta',       6800,  'industrial'),
    ('3500 Lenox Rd NE, Atlanta, GA',          'Atlanta',       3700,  'office'),
    ('400 Park Ave, New York, NY',             'New York',      8200,  'retail'),
    ('10 W 33rd St, New York, NY',             'New York',      9500,  'office'),
    ('6550 Hollywood Blvd, Los Angeles, CA',   'Los Angeles',   5100,  'retail'),
    ('2000 E Imperial Hwy, Los Angeles, CA',   'Los Angeles',   7900,  'industrial'),
    ('1888 Century Park E, Los Angeles, CA',   'Los Angeles',   4400,  'office'),
    ('4800 Main St, Kansas City, MO',          'Kansas City',   3900,  'retail'),
    ('7000 E 12th St, Kansas City, MO',        'Kansas City',   6100,  'industrial'),
    ('1 Convention Plaza, St. Louis, MO',      'St. Louis',     4700,  'retail'),
    ('800 Market St, Philadelphia, PA',        'Philadelphia',  5300,  'retail'),
    ('1500 Market St, Philadelphia, PA',       'Philadelphia',  6600,  'office'),
    ('200 Galleria Pkwy, Atlanta, GA',         'Atlanta',       4900,  'retail');

-- -----------------------------------------------------------------------------
-- Sample financial records — one row per property
-- -----------------------------------------------------------------------------
INSERT INTO financials (property_id, revenue, net_income, expenses) VALUES
    (1,  980000,  420000,  560000),
    (2,  1450000, 680000,  770000),
    (3,  720000,  290000,  430000),
    (4,  1100000, 510000,  590000),
    (5,  1620000, 740000,  880000),
    (6,  640000,  255000,  385000),
    (7,  890000,  390000,  500000),
    (8,  1530000, 710000,  820000),
    (9,  810000,  345000,  465000),
    (10, 2100000, 990000,  1110000),
    (11, 1880000, 850000,  1030000),
    (12, 1150000, 530000,  620000),
    (13, 1740000, 790000,  950000),
    (14, 960000,  415000,  545000),
    (15, 870000,  375000,  495000),
    (16, 1350000, 620000,  730000),
    (17, 1040000, 470000,  570000),
    (18, 1180000, 545000,  635000),
    (19, 1490000, 680000,  810000),
    (20, 920000,  400000,  520000);
