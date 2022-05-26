from django.shortcuts import render
from apps.cinema.models import Movie, Person, PersonMovie, MovieRating
from apps.authentication.models import User
from django.core.paginator import Paginator
from django.template.defaulttags import register
from django.db.models import Max, Avg


def movies(request):
    list_movies = Movie.objects.prefetch_related('persons').order_by('name')
    data = []
    for movie in list_movies:
        temp = {
            'imdb_id': movie.imdb_id,
            'name': movie.name
        }
        directors = Person.objects.filter(
            movies__imdb_id=movie.imdb_id, personmovie__category="director"
        ).all()
        if directors.count() > 0:
            temp['directors'] = ''
            for d in directors:
                temp['directors'] += d.name + ','
        else:
            temp['directors'] = '*no_directors*,'
        temp['directors'] = temp['directors'][:-1]
        temp['year'] = str(movie.year)[0:4]
        temp['genres'] = movie.genres.split(',')
        data.append(temp)
    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    user = request.user
    return render(request, 'cinema/movies.html', {
        'title': 'Movies List',
        'page_active': 'movies',
        'page_obj': page_obj,
        'b_page_number': page_number if page_number is not None else 1,
        'user': user,
    })


def movie_detail(request, imdb_id, edit_save=2, b_page_number=1):
    user = request.user
    if request.POST:
        if request.POST.get('rating-stars'):
            MovieRating.objects.create(movie=Movie.objects.get(imdb_id=imdb_id), user=User.objects.get(id=user.pk), value=request.POST.get('rating-stars'))
            avg = MovieRating.objects.filter(movie=imdb_id).aggregate(Avg('value'))['value__avg']
            Movie.objects.filter(imdb_id=imdb_id).update(rating_value=avg)
        else:
            edit_movie = Movie.objects.filter(imdb_id=imdb_id)
            edit_movie.update(name=request.POST.get('movie_name'))
            edit_movie.update(genres=request.POST.get('movie_genres'))
            year = request.POST.get('movie_year')
            if len(year) == 4 and year != '0000':
                try:
                    tmp = int(year)
                    edit_movie.update(year=year + '-01-01')
                except ValueError as e:
                    edit_movie.update(year='1111-01-01')
            else:
                edit_movie.update(year='1111-01-01')
            for p_m in PersonMovie.objects.filter(movie_id=imdb_id, category="director"):
                p_m.delete()
            for i_p in request.POST.get('imdb_persons').split(','):
                if i_p != '':
                    if PersonMovie.objects.filter(movie_id=imdb_id, person_id=i_p, category="director").count() == 0:
                        new_order = PersonMovie.objects.filter(movie_id=imdb_id).aggregate(Max("order"))['order__max']
                        if new_order is None:
                            new_order = 1
                        else:
                            new_order += 1
                        PersonMovie.objects.create(movie=Movie.objects.get(imdb_id=imdb_id), person=Person.objects.get(imdb_id=i_p), order=new_order, category="director", job="", characters="\\N")
    movie = Movie.objects.filter(imdb_id=imdb_id).first()
    id_not_found: str = ''
    data = {}
    if not movie:
        id_not_found = 'Movie with id "' + str(imdb_id) + '" not found...'
    else:
        rating = Movie.objects.get(imdb_id=imdb_id).rating_value
        is_voted = False
        if user.pk:
            values = MovieRating.objects.filter(movie_id=imdb_id, user_id=user.pk)
            if values.count() > 0:
                is_voted = True
        data = {
            'imdb_id': movie.imdb_id,
            'name': movie.name,
            'genres': movie.genres.split(','),
            'director': '',
            'year': str(movie.year)[0:4],
            'rating': rating if rating else 0.0,
            'is_voted': is_voted,
            'participants': [],
        }
        participants = Person.objects.filter(personmovie__movie_id=movie.imdb_id).order_by('name')
        if participants.count() > 0:
            directors = Person.objects.filter(personmovie__movie_id=movie.imdb_id, personmovie__category="director").all()
            if directors.count() > 0:
                for d in directors:
                    data['director'] += d.name + ','
            else:
                data['director'] = '*no_directors*,'
            data['director'] = data['director'][:-1]
            for p in participants:
                p_m = PersonMovie.objects.filter(movie_id=imdb_id, person_id=p.imdb_id).first()
                for old, new in {'\n': '', '\\N': '-', '"': '', '[': '', ']': ''}.items():
                    p_m.characters = p_m.characters.replace(old, new)
                temp = {
                    'imdb_id': p.imdb_id,
                    'name': p.name,
                    'position': PersonMovie.objects.filter(movie_id=movie.imdb_id, person_id=p.imdb_id).first().category,
                    'role': p_m.characters,
                }
                data['participants'].append(temp)
        data['list_all_person'] = Person.objects.prefetch_related().order_by('name')
    return render(request, 'cinema/movie_detail.html', {
        'title': 'Movie Detail',
        'page_active': 'movies',
        'id_not_found': id_not_found,
        'edit_save': edit_save,
        'b_page_number': b_page_number,
        'data': data,
        'user': user,
    })


@register.filter
def remove_last_comma(genres):
    if len(genres) > 0:
        res = ''
        for g in genres:
            res += g + ','
        res = res[:-1]
        return res
    return ''


@register.filter
def is_nodirector_in_movie(person_imdb_id, movie_imdb_id):
    if PersonMovie.objects.filter(movie_id=movie_imdb_id, person_id=person_imdb_id).exclude(category="director").count() > 0:
        return True
    return False


@register.filter
def is_disabled(person_imdb_id, movie_participants):
    for participant in movie_participants:
        if person_imdb_id == participant['imdb_id']:
            return 'disabled'
    return ''


def persons(request):
    return render(request, 'cinema/persons.html',
                  {'title': 'Persons List', 'page_active': 'persons'})


def person_detail(request, imdb_id):
    person = Person.objects.get(imdb_id=imdb_id)
    rat_person = person.movies.filter(rating_value__gt=0.0).aggregate(Avg('rating_value'))['rating_value__avg']
    return render(request, 'cinema/person_detail.html', {
        'title': 'Person Detail',
        'page_active': 'persons',
        'person_name': person.name,
        'rat_person': rat_person if rat_person else 0.0,
    })
