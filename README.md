# gmlz
An attempt to develop utilities for handling large GML-files

## gmlz format
The gmlz format is a carefully composed zip-file containing a gml file *and* an
index that can be used when reading the content.

The index is stored as a SQLite database with tables described below.

That's it - about the storage format.

## index (SQLite database)

```sql
create table xmlns(
      signature integer primary key
    , uri varchar
);
create table qname(
      signature integer primary key
    , namespace integer
    , localname varchar
);
create table xml_path(
      signature integer primary key
    , parent_signature integer
    , qname integer
);
create table xml_fragment(
      position integer primary key
    , size integer
    , gml_id varchar
    , xml_path integer
);
create table compressed_block(
      position integer primary key
    , size integer
    , compressed_position integer
    , compressed_size integer
);

```


Column | Data type | Description
--- | --- | ---
gml_id |
path | asdf



## utilities

### gmlzip

### gmlunzip
