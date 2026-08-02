## photo-db

### Photo storage

The pictures should be in a folder on the root of the repository called `photo_folder`. This can also be a link to the actual photo folder database. Photos should be organized in the following way:

> `./photo_folder/<year>/<theme>/IMG_<DATEFORMAT>.heic`

This path will be parsed and used as metadata, so it is strictly enforced. For example, a picture of a car on 2025 could be:

`./photo_folder/2025/Cars on the street/IMG_20250326_135342.heic`


### Get started

In order to start the program you need a `config.yml` file in the root of the repository, next to `main.py`. This YAML file should contain at least these variables:

```yaml
# Where the database file will be generated, saved and read. Can be absolute or relative
database_file: "db.json"
```

Do `./run_analyze.sh` for the database to be created or updated.

Do `./run_server` for the backend of the web client to be started up. Then you can open `./web_client/index.html` in a web browser to look at the pictures and search.
