DROP table IF EXISTS bibliography;
CREATE TABLE 'bibliography' (
		'id'		    INTEGER PRIMARY KEY AUTOINCREMENT,
		'abbreviation'	TEXT,
		'description' 	TEXT NOT NULL, -- json or bibtex entry
		'added_by'	    INTEGER NOT NULL,
		'project_type'  TEXT DEFAULT 'default'
);
INSERT INTO sqlite_sequence (name, seq) VALUES ('bibliography', 500); -- set start value for autoincrement to 501
		
