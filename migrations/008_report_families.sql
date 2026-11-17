ALTER TABLE crosses ADD COLUMN access_level TEXT;
ALTER TABLE crosses ADD COLUMN report_family_id TEXT;
CREATE TABLE cross_report_sources(
 cross_id TEXT NOT NULL REFERENCES crosses(id),
 source_id TEXT NOT NULL REFERENCES sources(id),
 relation TEXT NOT NULL,
 PRIMARY KEY(cross_id,source_id)
);
