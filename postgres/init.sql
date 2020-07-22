SELECT 'CREATE DATABASE shhh'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'shhh')\gexec
