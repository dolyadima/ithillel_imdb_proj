import os.path
from django.core.management.base import BaseCommand
from ...models import Person


class Command(BaseCommand):
    help = "Imports persons from tsv file"

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
                if not line.startswith("nm"):
                    continue
                data = line.split("\t")

                imdb_id = data[0]

                if data[2] == "\\N":
                    data[2] = None
                else:
                    data[2] = f"{data[2]}-01-01"

                if data[3] == "\\N":
                    data[3] = None
                else:
                    data[3] = f"{data[3]}-01-01"

                person_data = {
                    "imdb_id": imdb_id,
                    "name": data[1],
                    "birth_year": data[2],
                    "death_year": data[3],
                }

                person, created = Person.objects.get_or_create(
                    imdb_id=imdb_id, defaults=person_data
                )

                if not created:
                    Person.objects.filter(imdb_id=person.imdb_id).update(**person_data)
