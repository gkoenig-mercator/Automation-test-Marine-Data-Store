# Database Schema and Usage
Currently, the database contains a single table with rows describing each download attempt, including errors.

## To connect:

```bash
psql -h HOST -p PORT -U USERNAME -d DATABASE_NAME
```

## List tables:

```bash
\dt
```

## Show first 10 rows:

```bash
SELECT * FROM my_table LIMIT 10;
```

## Show last 10 rows:

```bash
SELECT * FROM my_table ORDER BY id DESC LIMIT 10;
```