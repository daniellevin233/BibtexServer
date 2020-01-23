CREATE TABLE 'bibliography' (
		'id'		        INTEGER PRIMARY KEY AUTOINCREMENT,
		'abbreviation'	TEXT,
		'description' 	TEXT NOT NULL, -- json or bibtex entry
		'added_by'	    INTEGER NOT NULL
);
		
