from requests import Session
from bs4 import BeautifulSoup

from ..utilities import get_sentiment_rating
from ..models import Review, ReviewType

class MetacriticProvider:
    def __init__(self):
        self.BASE_URL = 'https://www.metacritic.com'

        self.session = Session()
        self.session.headers.update(
            {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'})

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
