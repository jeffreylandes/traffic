# Traffic

This is an experimental repository which seeks to provide traffic values (and high-quality predictions where missing data exists) for the purpose of understanding noise trends in Minnesota.

## Why Minnesota?

Simply: they have easily accessible data.

## Eventual Structure
```
| migrations/
| scripts/ 
| lambda/
Makefile
```

In which the Makefile executes a series of `scripts` to create a completely processed database. Then a series of `migrations` can be run to create the table followed by (ideally) a simple `ogr2ogr` command to copy the data in the final file to the table. A simple `lambda` through API Gateway will provide functionality for a simple GET request based on the specified bounds in the front-end.

## To Dos
- [ ] Create AWS RDS resource
- [ ] Migrate data to RDS Postgres/PostGIS
- [ ] Set up ML infrastructure to train GraphCNN 
- [ ] Create an API which allows a user to GET data within a specified bounds
