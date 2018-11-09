
CREATE TABLE stat_context (

  id         SERIAL PRIMARY KEY,
  value      VARCHAR(200) UNIQUE

);

CREATE TABLE stat_target (

  id         SERIAL PRIMARY KEY,
  value      VARCHAR(200) UNIQUE

);


CREATE TABLE stat (

  id         SERIAL PRIMARY KEY,
  context_id INT REFERENCES stat_context(id),
  target_id  INT REFERENCES stat_target(id),

  value      VARCHAR(200),
  ts         TIMESTAMP DEFAULT now()

);



CREATE TABLE event_context (

  id         SERIAL PRIMARY KEY,
  value      VARCHAR(200) UNIQUE

);

CREATE TABLE event_target (

  id         SERIAL PRIMARY KEY,
  value      VARCHAR(200) UNIQUE

);


CREATE TABLE event (

  id         SERIAL PRIMARY KEY,
  context_id INT REFERENCES event_context(id),
  target_id  INT REFERENCES event_target(id),

  value      VARCHAR(200),
  ts         TIMESTAMP DEFAULT now()

);
