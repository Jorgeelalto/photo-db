from photodb import photodb


p = photodb.PhotoDB('config.yml')
p.load()
# Looks for photo files and adds them to database
p.scan()

# Extracts file metadata
p.extract_exif_all(overwrite=False)
# Transforms pic coordinates into a human-readable location
p.resolve_location_all(overwrite=False)
# Infers a description and a set of tags from the image
p.describe_all(overwrite=False)

p.save()
exit(0)
