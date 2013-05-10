ALTER TABLE document ADD COLUMN year INTEGER;
UPDATE document SET year = SUBSTR(publication_date, 7)::int;


