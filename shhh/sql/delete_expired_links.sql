DELETE
FROM links
WHERE date_expires <= now();
