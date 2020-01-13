-- -*- coding: utf-8 -*-
-- File  : initialize.sql
-- Author: Austin Schaffer <schaffer.austin.t@gmail.com>
-- Date  : 18.09.2019
-- Last edit by : Matthieu Petiteau <mpetiteau.pro@gmail.com> on 12.01.2020
--                Remove event_scheduler as deletions are managed by Celery
-- Desc  : Initializes tables, settings, and events for the MySQL instance.

CREATE TABLE IF NOT EXISTS `links` (
  `slug_link` text,
  `encrypted_text` text,
  `date_created` datetime DEFAULT NULL,
  `date_expires` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
