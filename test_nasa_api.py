from datetime import date
from random import randint
import requests
from settings import API_KEY, URL


current_date = date.today().strftime('%Y-%m-%d')
default_params = {'api_key': API_KEY, 'date': current_date}


def generate_random_date_from_2015_to_2020():
    return date(randint(2015, 2020), randint(1, 12), randint(1, 28)).strftime('%Y-%m-%d')


class TestNasaAPI:
    def test_request_without_api_key(self):
        with requests.get(URL) as response:
            body = response.json()
            assert all((response.status_code == 403, body['error']['code'] == 'API_KEY_MISSING'))

    def test_invalid_date_format(self):
        with requests.get(URL, params={'api_key': API_KEY, 'date': date.today().strftime('%d-%m-%y')}) as response:
            assert all((response.status_code == 400, "does not match format '%Y-%m-%d" in response.json()['msg']))

    def test_check_url_for_image_in_response(self):
        with requests.get(URL, params=default_params) as response:
            url_image = response.json()['url']
            with requests.get(url_image) as resp:
                assert resp.status_code == 200

    def test_check_url_for_hd_image_in_response(self):
        with requests.get(URL, params=default_params) as response:
            url_image = response.json()['hdurl']
            with requests.get(url_image) as resp:
                assert resp.status_code == 200

    def test_different_pictures_for_different_dates(self):
        image_for_current_date = requests.get(URL, params=default_params).json()['url']

        random_date = generate_random_date_from_2015_to_2020()
        image_for_different_date = requests.get(URL, params={'api_key': API_KEY, 'date': random_date}).json()['url']

        assert image_for_current_date != image_for_different_date

    def test_invalid_date_use_with_start_date(self):
        random_date = date(randint(2015, 2020), randint(1, 12), randint(1, 28)).strftime('%Y-%m-%d')
        with requests.get(URL, params={'api_key': API_KEY,
                                       'default_params': current_date,
                                       'start_date': random_date}) as response:
            assert response.status_code == 400

    def test_without_current_date(self):
        with requests.get(URL, params={'api_key': API_KEY}) as response:
            assert response.json()['date'] == current_date

    def test_explanation_len_bigger_then_zero(self):
        with requests.get(URL, params=default_params) as response:
            assert len(response.json()['explanation']) > 0

    def test_media_type_is_image(self):
        """
        Test  with error.
        Media type must be image
        """
        with requests.get(URL, params=default_params) as response:
            assert response.json()['media_type'] == 'video'

    def test_len_of_response_with_count(self):
        """
        Test with error.
        Length of body must be equal to parameter 'count'
        """
        count = randint(1, 10)
        with requests.get(URL, params={'api_key': API_KEY, 'count': count}) as response:
            assert count != len(response.json())
