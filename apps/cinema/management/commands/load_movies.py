import os.path
from django.core.management.base import BaseCommand
from ...models import Movie


class Command(BaseCommand):
    help = "Imports movies from tsv file"

    def add_arguments(self, parser):
        parser.add_argument("-f", "--file", type=str, required=True)

    def handle(self, *a, **kwa):
        file_name = kwa.get("file")

        if not os.path.exists(file_name):
            print("No file exists.")

        with open(file_name, encoding="utf-8") as f:
            for line in f.readlines():
                if not line:
                    continue
                if not line.startswith("tt"):
                    continue
                data = line.split("\t")

                if data[1] not in ("movie", "short"):
                    continue
                date = data[5]

                if date == "\\N":
                    date = None
                else:
                    date = f"{date}-01-01"

                movie_data = {
                    "title_type": data[1],
                    "name": data[2],
                    "is_adult": data[4] == "1",
                    "year": date,
                    "genres": data[8],
                }

                movie, created = Movie.objects.get_or_create(
                    imdb_id=data[0], defaults=movie_data
                )

                if created:
                    Movie.objects.filter(imdb_id=movie.imdb_id).update(**movie_data)
