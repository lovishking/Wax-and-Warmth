# Local database archive

`outer-backend-before-consolidation.sqlite3` is a verified copy of the SQLite database from the former `D:\wax-and-warmth\backend` folder. It contains a separate 12-product catalog and local user records. `legacy-repo-db-before-cleanup.sqlite3` preserves the older Django database that used to sit at `backend/db.sqlite3`.

The active app continues to use `backend/dev.sqlite3`. These archives are recovery copies; their catalog and account data were not merged into the active database.

SQLite files are excluded from Git. Keep this archive local and do not upload it to the public repository.
