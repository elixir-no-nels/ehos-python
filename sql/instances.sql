CREATE TABLE node_state (

  id         SERIAL PRIMARY KEY,
  name      VARCHAR(200) UNIQUE
);

CREATE TABLE vm_state (

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
  image          VARCHAR(80) NOT NULL,

  cloud_id       INT REFERENCES cloud(id),
  node_state_id  INT REFERENCES node_state(id),
  vm_state_id    INT REFERENCES vm_state(id)
);


CREATE TABLE setting (
  id             SERIAL PRIMARY KEY,

  name           VARCHAR(80) NOT NULL,
  value          VARCHAR(80) NOT NULL
);
