import os.path
from django.core.management.base import BaseCommand, CommandError
from ...models import Movie, Person, PersonMovie


class Command(BaseCommand):
    help = "Imports personmovies from tsv file"

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

                person = Person.objects.filter(imdb_id=data[2]).first()
                if not person:
                    continue

                movie = Movie.objects.filter(imdb_id=data[0]).first()
                if not movie:
                    continue

                pm_data = {
                    "order": int(data[1]),
                    "category": data[3],
                    "job": data[4] if data[4] != "\\N" else "",
                    "characters": data[5] if data[5] != "\\N" else "",
                }

                PersonMovie.objects.get_or_create(
                    movie=movie, person=person, defaults=pm_data
                )
