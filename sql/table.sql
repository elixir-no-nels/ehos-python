drop database IF EXISTS ehos_1_0_0 ;
create database ehos_1_0_0;
use ehos_1_0_0;

CREATE TABLE status (
  id            INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  description   VARCHAR(80) NOT NULL,
  UNIQUE KEY `description` (`description`)

) ENGINE=InnoDB;


INSERT INTO status (description) VALUES ('booting', 'idle', 'busy', 'destroyed');


CREATE TABLE node (
  id            INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  status_id     INT,
  uuid          VARCHAR(80) NOT NULL,
  name          VARCHAR(80) NOT NULL,
  creation      datetimestamp,
  destruction   datetimestamp,

  FOREIGN KEY (status_id)
        REFERENCES status(id),

) ENGINE=InnoDB;
