from photodb import photodb

p = photodb.PhotoDB('config.yml')
p.scan()
p.extract_exif_all()
p.save()
print(p)
