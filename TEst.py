import requests
import re
from bs4 import BeautifulSoup


url = 'https://www.imdb.com/title/tt0119094/fullcredits?ref_=tt_cl_sm'
headers = {'Accept-Language': 'en',
            'X-FORWARDED-FOR': '2.21.184.0'}


def get_actors_by_movie_soup(cast_page_soup, num_of_actors_limit=None):
    n = num_of_actors_limit
    soup = BeautifulSoup(cast_page_soup.text)
    cast = soup.find_all('table', {'class': 'cast_list'})
    actors = []
    for line in cast:
        res = line.find_all('td', {'class': None})

    for actor in res:
        actors.append([actor.find('a').text[1:-1], 'https://www.imdb.com' + actor.find('a').get('href')])

    if n != None:
        return actors[:n]
    else:
        return actors


get_actors_by_movie_soup(requests.get(url, headers=headers), 7)


def get_movies_by_actor_soup(actor_page_soup, num_of_movies_limit=None):
    n = num_of_movies_limit
    soup = BeautifulSoup(actor_page_soup.text)
    filmography = soup.find('div', {'class': 'filmo-category-section'})
    films = filmography.find_all('div', {'class': re.compile('filmo-row+')})
    res = []
    for film in films:
        if len(re.findall('\(', film.contents[4])) == 0:
            res.append([film.find('b').find('a').text ,'https://www.imdb.com' + film.find('b').find('a').get('href')])
    if n != None:
        return res[:n]
    else:
        return res


get_movies_by_actor_soup(requests.get(url, headers=headers), 4)


def get_movie_distance(actor_start_url, actor_end_url, num_of_actors_limit=None, num_of_movies_limit=None):
    target_actor = BeautifulSoup(requests.get(actor_end_url).text).find('span', {'class': 'itemprop'}).text
    current_distance = 1
    checked_movies = set()
    checked_actors_links = set()
    checked_actors = set()

    actor_movies_list = get_movies_by_actor_soup(requests.get(actor_start_url, headers=headers), num_of_movies_limit)

    for _ in range(11):

        for movie in actor_movies_list:

            if movie[0] not in checked_movies:

                response = requests.get(movie[1], headers=headers)
                soup = BeautifulSoup(response.content)
                cast = get_actors_by_movie_soup(requests.get(movie[1] + soup.find('a',
                                                                                  {
                                                                                      'class': 'ipc-link ipc-link--baseAlt ipc-link--inherit-color'
                                                                                  }
                                                                                  )['href'],
                                                             headers=headers), num_of_actors_limit)
                checked_movies.add(movie[0])

            for actor in cast:

                checked_actors_links.add(actor[1])
                checked_actors.add(actor[0])


                if target_actor in checked_actors:
                    return current_distance

        actor_movies_list = []
        current_distance += 1
        if current_distance > 3:
            return -1

        for actor in checked_actors_links:
            actor_movies_list += get_movies_by_actor_soup(requests.get(actor, headers=headers), num_of_movies_limit)


get_movie_distance('https://imdb.com/name/nm0425005/?ref_=nv_sr_srsg_0', 'https://www.imdb.com/name/nm4862056/?ref_=ttfc_fc_cl_t2', 5, 5)
