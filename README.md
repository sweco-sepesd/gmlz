# gmlz
An attempt to develop utilities for handling large GML-files

## gmlz format
The gmlz format is a carefully composed zip-file containing a gml file *and* an
index that can be used when reading the content.

The index is stored as a SQLite database with tables described below.

That's it - about the storage format.

## index (SQLite database)

```sql
create table gml_id(pos integer primary key, gml_id )
```


Column | Data type | Description
--- | --- | ---
gml_id |
path | asdf



## utilities

### gmlzip

### gmlunzip
