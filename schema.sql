
DROP TABLE if exists public."Fill";
DROP TABLE if exists public."StationFuel";
DROP TABLE if exists public."Fuel";
DROP TABLE if exists public."Business";
DROP TABLE if exists public."Ownership";
DROP TABLE if exists public."Vehicle";
DROP TABLE if exists public."VehicleModel";
DROP TABLE if exists public."User";
DROP TABLE if exists public."State";
DROP TABLE if exists public."Country";
DROP SEQUENCE if exists user_id_seq;
DROP SEQUENCE if exists model_id_seq;
DROP SEQUENCE if exists vehicle_id_seq;



CREATE TABLE public."Country"
(
  id integer NOT NULL,
  name character varying(120),
  abbrev character varying(20),
  CONSTRAINT "Country_pkey" PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);


CREATE TABLE public."State"
(
  id integer NOT NULL,
  country integer,
  name character varying(120),
  abbrev character varying(20),
  CONSTRAINT "State_pkey" PRIMARY KEY (id),
  CONSTRAINT "State_country_fkey" FOREIGN KEY (country)
      REFERENCES public."Country" (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);

CREATE SEQUENCE user_id_seq;

CREATE TABLE public."User"
(
  userid integer NOT NULL DEFAULT NEXTVAL('user_id_seq'),
  phone character varying(20),
  email character varying(120),
  password character varying(64) NOT NULL,
  token character varying(64),
  city character varying,
  stateid integer,
  zip character varying(20),
  specialoffers boolean,
  validated boolean,
  CONSTRAINT "User_pkey" PRIMARY KEY (userid),
  CONSTRAINT "User_email_key" UNIQUE (email)
)
WITH (
  OIDS=FALSE
);

CREATE SEQUENCE model_id_seq;

CREATE TABLE public."VehicleModel"
(
  modelid integer NOT NULL DEFAULT NEXTVAL('model_id_seq'),
  vintag character(10) NOT NULL,
  make character varying(100),
  model character varying(100),
  year integer,
  vehicle_type character varying(100),
  engine_cylinders integer,
  engine_liters real,
  horse_power integer,
  drive_type character varying(20),
  jpg character varying(100),
  CONSTRAINT "VehicleModel_pkey" PRIMARY KEY (modelid)
)
WITH (
  OIDS=FALSE
);

CREATE SEQUENCE vehicle_id_seq;

CREATE TABLE public."Vehicle"
(
  vid integer NOT NULL DEFAULT NEXTVAL('vehicle_id_seq'),
  vin character(17) NOT NULL,
  modelid integer,
  initialodo real,
  CONSTRAINT "Vehicle_pkey" PRIMARY KEY (vid),
  CONSTRAINT "Vehicle_modelid_fkey" FOREIGN KEY (modelid)
      REFERENCES public."VehicleModel" (modelid) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);

CREATE TABLE public."Ownership"
(
  userid integer NOT NULL,
  vid integer NOT NULL,
  vehicle_name character varying(40),
  start_date date,
  CONSTRAINT "Ownership_pkey" PRIMARY KEY (userid, vid),
  CONSTRAINT "Ownership_vid_fkey" FOREIGN KEY (vid)
      REFERENCES public."Vehicle" (vid) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT "Ownership_userid_fkey" FOREIGN KEY (userid)
      REFERENCES public."User" (userid) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);

CREATE TABLE public."Business"
(
  id integer NOT NULL,
  longitude real,
  latitude real,
  street character varying(100),
  city character varying(120),
  stateid integer,
  zip character varying(20),
  name character varying(120),
  CONSTRAINT "Business_pkey" PRIMARY KEY (id),
  CONSTRAINT "Business_stateid_fkey" FOREIGN KEY (stateid)
      REFERENCES public."State" (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);

CREATE TABLE public."Fuel"
(
  id integer NOT NULL,
  grade character varying(20),
  description character varying(100),
  CONSTRAINT "Fuel_pkey" PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);

CREATE TABLE public."StationFuel"
(
  id integer NOT NULL,
  price real,
  effdate date,
  stationid integer,
  fuelid integer,
  CONSTRAINT "StationFuel_pkey" PRIMARY KEY (id),
  CONSTRAINT "StationFuel_fuelid_fkey" FOREIGN KEY (fuelid)
      REFERENCES public."Fuel" (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT "StationFuel_stationid_fkey" FOREIGN KEY (stationid)
      REFERENCES public."Business" (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT "StationFuel_effdate_stationid_fuelid_key" UNIQUE (effdate, stationid, fuelid)
)
WITH (
  OIDS=FALSE
);

CREATE TABLE public."Fill"
(
  odo real NOT NULL,
  vid integer NOT NULL,
  stationfuelid integer NOT NULL,
  gallons real,
  date date,
  filledtank boolean, -- This indicates the tank was completely filled after this fill.
  CONSTRAINT "Fill_pkey" PRIMARY KEY (odo, vid, stationfuelid),
  CONSTRAINT "Fill_stationfuelid_fkey" FOREIGN KEY (stationfuelid)
      REFERENCES public."StationFuel" (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT "Fill_vid_fkey" FOREIGN KEY (vid)
      REFERENCES public."Vehicle" (vid) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);

COMMENT ON COLUMN public."Fill".filledtank IS 'This indicates the tank was completely filled after this fill.';

INSERT INTO "VehicleModel" (vintag, make) VALUES ('UnknownVIN', 'Unknown Vehicle Make & Model');
INSERT INTO "VehicleModel" (vintag, make) VALUES ('InvalidVIN', 'Invalid VIN');
INSERT INTO "Country" (id, name, abbrev) VALUES (0, 'United States of America', 'USA');
INSERT INTO "State" (id, country, name, abbrev) VALUES (0, 0, 'Iowa', 'IA');
INSERT INTO "State" (id, country, name, abbrev) VALUES (1, 0, 'Minnesota', 'MN');
INSERT INTO "State" (id, country, name, abbrev) VALUES (2, 0, 'Wisconsin', 'WI');
INSERT INTO "State" (id, country, name, abbrev) VALUES (3, 0, 'Illinois', 'IL');
INSERT INTO "State" (id, country, name, abbrev) VALUES (4, 0, 'Indiana', 'IN');
INSERT INTO "State" (id, country, name, abbrev) VALUES (5, 0, 'Kentucky', 'KY');
INSERT INTO "State" (id, country, name, abbrev) VALUES (6, 0, 'Arkansas', 'AR');
INSERT INTO "State" (id, country, name, abbrev) VALUES (7, 0, 'Alaska', 'AK');
INSERT INTO "State" (id, country, name, abbrev) VALUES (8, 0, 'Ohio', 'OH');
INSERT INTO "State" (id, country, name, abbrev) VALUES (9, 0, 'Louisiana', 'LA');
INSERT INTO "State" (id, country, name, abbrev) VALUES (10, 0, 'Alabama', 'AL');
INSERT INTO "State" (id, country, name, abbrev) VALUES (11, 0, 'Georgia', 'GA');
INSERT INTO "State" (id, country, name, abbrev) VALUES (12, 0, 'South Carolina', 'SC');
INSERT INTO "State" (id, country, name, abbrev) VALUES (13, 0, 'North Carolina', 'NC');
INSERT INTO "State" (id, country, name, abbrev) VALUES (14, 0, 'Michigan', 'MI');
INSERT INTO "State" (id, country, name, abbrev) VALUES (15, 0, 'Pennsylvania', 'PA');
INSERT INTO "State" (id, country, name, abbrev) VALUES (16, 0, 'Vermont', 'VT');
INSERT INTO "State" (id, country, name, abbrev) VALUES (17, 0, 'New Hampshire', 'NH');
INSERT INTO "State" (id, country, name, abbrev) VALUES (18, 0, 'Maine', 'ME');
INSERT INTO "State" (id, country, name, abbrev) VALUES (19, 0, 'New York', 'NY');
INSERT INTO "State" (id, country, name, abbrev) VALUES (20, 0, 'Delaware', 'DE');
INSERT INTO "State" (id, country, name, abbrev) VALUES (21, 0, 'Maryland', 'MD');
INSERT INTO "State" (id, country, name, abbrev) VALUES (22, 0, 'Connecticut', 'CT');
INSERT INTO "State" (id, country, name, abbrev) VALUES (23, 0, 'Massachusetts', 'MA');
INSERT INTO "State" (id, country, name, abbrev) VALUES (24, 0, 'Virginia', 'VA');
INSERT INTO "State" (id, country, name, abbrev) VALUES (25, 0, 'West Virginia', 'WV');
INSERT INTO "State" (id, country, name, abbrev) VALUES (26, 0, 'Mississippi', 'MS');
INSERT INTO "State" (id, country, name, abbrev) VALUES (27, 0, 'Oklahoma', 'OK');
INSERT INTO "State" (id, country, name, abbrev) VALUES (28, 0, 'North Dakota', 'ND');
INSERT INTO "State" (id, country, name, abbrev) VALUES (29, 0, 'South Dakota', 'SD');
INSERT INTO "State" (id, country, name, abbrev) VALUES (30, 0, 'Nebraska', 'NE');
INSERT INTO "State" (id, country, name, abbrev) VALUES (31, 0, 'Kansas', 'KS');
INSERT INTO "State" (id, country, name, abbrev) VALUES (32, 0, 'Texas', 'TX');
INSERT INTO "State" (id, country, name, abbrev) VALUES (33, 0, 'New Mexico', 'NM');
INSERT INTO "State" (id, country, name, abbrev) VALUES (34, 0, 'Colorado', 'CO');
INSERT INTO "State" (id, country, name, abbrev) VALUES (35, 0, 'Wyoming', 'WY');
INSERT INTO "State" (id, country, name, abbrev) VALUES (36, 0, 'Montana', 'MT');
INSERT INTO "State" (id, country, name, abbrev) VALUES (37, 0, 'Idaho', 'ID');
INSERT INTO "State" (id, country, name, abbrev) VALUES (38, 0, 'Utah', 'UT');
INSERT INTO "State" (id, country, name, abbrev) VALUES (39, 0, 'Nevada', 'NV');
INSERT INTO "State" (id, country, name, abbrev) VALUES (40, 0, 'Arizona', 'AZ');
INSERT INTO "State" (id, country, name, abbrev) VALUES (41, 0, 'California', 'CA');
INSERT INTO "State" (id, country, name, abbrev) VALUES (42, 0, 'Oregon', 'OR');
INSERT INTO "State" (id, country, name, abbrev) VALUES (43, 0, 'Washington', 'WA');
INSERT INTO "State" (id, country, name, abbrev) VALUES (44, 0, 'Hawaii', 'HI');
INSERT INTO "State" (id, country, name, abbrev) VALUES (45, 0, 'Florida', 'FL');
INSERT INTO "State" (id, country, name, abbrev) VALUES (46, 0, 'Missouri', 'MO');
INSERT INTO "State" (id, country, name, abbrev) VALUES (47, 0, 'New Jersey', 'NJ');
INSERT INTO "State" (id, country, name, abbrev) VALUES (48, 0, 'Tennessee', 'TN');
INSERT INTO "State" (id, country, name, abbrev) VALUES (49, 0, 'Rhode Island', 'RI');

