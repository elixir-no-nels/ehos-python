-- noinspection SqlNoDataSourceInspectionForFile


CREATE TABLE node_status (

  id         SERIAL PRIMARY KEY,
  name      VARCHAR(200) UNIQUE

);

CREATE TABLE node_state (

  id         SERIAL PRIMARY KEY,
  name      VARCHAR(200) UNIQUE

);

CREATE TABLE cloud (
  id            SERIAL PRIMARY KEY,

  name          VARCHAR(80) NOT NULL

);


CREATE TABLE node (
  id             SERIAL PRIMARY KEY,

  uuid           VARCHAR(80) NOT NULL,
  name           VARCHAR(80) NOT NULL,

  cloud_id       INT REFERENCES cloud(id),
  node_status_id INT REFERENCES node_status(id),
  node_state_id  INT REFERENCES node_state(id)
);


