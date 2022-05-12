from django.db import models
from django.utils.translation import gettext_lazy as _


class Movie(models.Model):  # title.basics.tsv
    TITLE_TYPE = [
        ("short", _("короткометражка")),
        ("movie", _("фильм")),
    ]
    imdb_id = models.CharField(_("MOVIE id"), primary_key=True, max_length=255)
    title_type = models.CharField(_("тип фильма"), max_length=255, choices=TITLE_TYPE)
    name = models.CharField(_("название фильма"), max_length=255)
    is_adult = models.BooleanField(_("18+"))
    year = models.DateField(_("дата релиза"), null=True)
    genres = models.CharField(_("жанры"), max_length=255)

    class Meta:
        verbose_name = "Movie"
        verbose_name_plural = "Movies"

    def __str__(self):
        return f'M<{self.name}>'


class Person(models.Model):  # name.basics.tsv
    imdb_id = models.CharField(_("PERSON id"), primary_key=True, max_length=255)
    name = models.CharField(_("имя актёра"), max_length=255)
    birth_year = models.DateField(_("дата рождения"), null=True)
    death_year = models.DateField(_("дата смерти"), null=True)
    movies = models.ManyToManyField(
        Movie, through="PersonMovie", related_name="persons"
    )

    class Meta:
        verbose_name = "Person"
        verbose_name_plural = "Persons"

    def __str__(self):
        return f'P<{self.name}>'


class PersonMovie(models.Model):  # title.principals.tsv
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    order = models.IntegerField(_("order"))
    category = models.CharField(_("category"), max_length=255)
    job = models.CharField(_("job"), max_length=255)
    characters = models.CharField(_("characters"), max_length=255)
