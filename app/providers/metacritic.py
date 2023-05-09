from requests import Session
from bs4 import BeautifulSoup

from ..utilities import get_sentiment_rating
from ..models import Genre, Review, ReviewType, Show

class MetacriticProvider:
    def __init__(self):
        self.BASE_URL = 'https://www.metacritic.com'

        self.session = Session()
        self.session.headers.update(
            {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'})

    def try_remove_image_size(self, url: str) -> str:
        from re import sub
        sanitzed_url = sub(r'-(\d{2})', '', url)

        request = self.session.get(sanitzed_url)

        if request.status_code == 200:
            return sanitzed_url

        return url

    def get_critic_reviews(self, show_id: int, provider_id: str) -> list:
        try:
            request = self.session.get(f'{self.BASE_URL}/tv/{provider_id}/critic-reviews')

            beautiful_soup = BeautifulSoup(request.text, 'lxml')
            posts = beautiful_soup.find_all('a', class_='no_hover')

            result = []

            for post in posts:
                review = Review()

                review.show_id = show_id
                review.created_by = ReviewType.CRITIC
                review.text = post.contents[-1].strip()
                review.score = get_sentiment_rating(review.text)

                result.append(review)

            return result
        except:
            return []

    def search_tv_shows(self, name: str) -> list:
        try:
            request = self.session.get(f'{self.BASE_URL}/search/tv/{name}/results')

            beautiful_soup = BeautifulSoup(request.text, 'lxml')
            tv_shows = beautiful_soup.find_all('div', class_='result_wrap')

            result = []

            for tv_show in tv_shows:
                title_element = tv_show.find('a', class_='')

                show = Show()

                show.provider_id = title_element.get('href').replace('/tv/', '')
                show.title = title_element.text.strip()
                show.thumbnail = self.try_remove_image_size(tv_show.find('img').get('src'))

                result.append(show)

            return result
        except Exception:
            return []

    def get_tv_show_info(self, show: Show):
        try:
            request = self.session.get(f'{self.BASE_URL}/tv/{show.provider_id}')
            beautiful_soup = BeautifulSoup(request.text, 'lxml')

            show.release_date = beautiful_soup.select('.release_date > span:nth-child(2)')[0].text.strip()
            show.summary = beautiful_soup.select('.summary_deck > span:nth-child(2)')[0].text.strip()

            genre_elements = beautiful_soup.select('.genres > span:nth-child(2)')[0].find_all('span')

            genres = []

            for genre_element in genre_elements:
                genre = Genre()

                genre.name = genre_element.text.strip()
                genre.show_id = show.id

                genres.append(genre)

            show.genres = genres

            return show
        except Exception:
            pass

    def get_user_reviews(self, show_id: int, provider_id: str) -> list:
        try:
            request = self.session.get(f'{self.BASE_URL}/tv/{provider_id}/user-reviews')

            beautiful_soup = BeautifulSoup(request.text, 'lxml')
            posts = beautiful_soup.find_all('div', class_='right fl')

            result = []

            for post in posts:
                blurb_element = post.select_one('.blurb_expanded')

                if not blurb_element or post.select_one('strong.bold'):
                    continue

                review = Review()

                review.show_id = show_id
                review.created_by = ReviewType.USER
                review.text = blurb_element.text.strip()
                review.score = get_sentiment_rating(review.text)

                result.append(review)

            return result
        except:
            return []
