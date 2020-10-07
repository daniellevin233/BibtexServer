DROP table IF EXISTS bibliography;
CREATE TABLE 'bibliography' (
		'id'		    INTEGER PRIMARY KEY AUTOINCREMENT,
		'abbreviation'	TEXT,
		'description' 	TEXT NOT NULL, -- json or bibtex entry
		'added_by'	    INTEGER NOT NULL,
		'project_type'  TEXT NOT NULL
);
UPDATE sqlite_sequence SET seq = 500 WHERE name = 'bibliography'; -- set start value for autoincrement to 501
		
