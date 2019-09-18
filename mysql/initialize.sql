-- -*- coding: utf-8 -*-
-- File  : initialize.sql
-- Author: Austin Schaffer <schaffer.austin.t@gmail.com>
-- Date  : 18.09.2019
-- Desc  : Initializes tables, settings, and events for the MySQL instance.

CREATE TABLE IF NOT EXISTS `links` (
  `slug_link` text,
  `passphrase` text,
  `encrypted_text` text,
  `date_created` datetime DEFAULT NULL,
  `date_expires` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

SET GLOBAL event_scheduler = ON;

CREATE EVENT IF NOT EXISTS AutoDeleteExpiredRecords
ON SCHEDULE
EVERY 2 HOUR
DO
  DELETE FROM `links` WHERE `date_expires` <= now();
