# Traffic

This is an experimental repository which seeks to provide traffic values (and high-quality predictions where missing data exists) for the purpose of understanding noise trends in Minnesota.

## Why Minnesota?

Simply: they have easily accessible data.

## Structure
```
| predictive/  # contains scripts to generative featurized data from a GeoPandas dataframe and infrastructure to train a GraphCNN model
| scripts/  # contains scripts to generate clean data, combining official Minnesota ADT values with OSM road data
Makefile
```

In which the Makefile executes a series of `scripts` to create completely processed training and validation data.

## Fetching data 
First you must set up a virtual environment with the necessary deps.
```shell script
pip install pipenv && pipenv install --dev
```
Then you may run the makefile.
```shell script
make prepare-data
```

## Database migrations 

```shell script
yoyo apply --database postgresql://postgres@localhost/traffic ./migrations
```

## To Dos
- [ ] Figure out how to host the data 
- [ ] Create an API which allows a user to GET data within a specified bounds
