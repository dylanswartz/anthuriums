ALTER TABLE crosses ADD COLUMN reported_result TEXT NOT NULL DEFAULT 'unknown';
ALTER TABLE crosses ADD COLUMN reported_endpoint TEXT NOT NULL DEFAULT 'unknown';
ALTER TABLE crosses ADD COLUMN identity_qualified INTEGER NOT NULL DEFAULT 0 CHECK(identity_qualified IN(0,1));
ALTER TABLE crosses ADD COLUMN graph_eligible INTEGER NOT NULL DEFAULT 0 CHECK(graph_eligible IN(0,1));
