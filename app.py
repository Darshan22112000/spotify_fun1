import requests
from flask import Flask, redirect, render_template
from authorization import Authorization
from flask_cors import CORS

import logging

from power_bi_refresh_2 import PowerBi2

app = Flask(__name__, static_url_path='/static', template_folder='/templates')
CORS(app)

app = Flask(__name__)

        @app.route('/')
        def home():
            # cls.logger.info('home here')
            return render_template('index.html')

        @app.route('/login')
        def login():
            # cls.logger.info('login here')
            res = redirect(url)
            return res

        @app.route('/logged_in')
        async def logged_in():
            params = Authorization.get_auth_params()
            redirect(params['redirect_url'])
            if params['response_type'] == 'code':
                res = await Authorization.set_auth_params()
            refresh = PowerBi2.refresh_report()
            if refresh['value']==1:
                return render_template('logged_in.html')
            else:
                return render_template('ops.html', status=refresh['status'], message=refresh['message'])
        @app.route('/get-top-user-tracks')
        def get_top_user_tracks():
            top_tracks, ids = MainTool.get_user_tracks()
            return top_tracks

        @app.route('/get-top-track-ids')
        def get_top_track_ids():
            top_tracks, ids = MainTool.get_user_tracks()
            # ids = ids.split(',')
            ids = []
            for item in top_tracks['items']:
                temp = {
                    'name': item['name'],
                    'id': item['id']
                }
                ids.append(temp)
            return ids

        @app.route('/get-track-features')
        def get_track_features():
            top_tracks, ids = MainTool.get_user_tracks()
            features = MainTool.get_tracks_audio_features(ids=ids)
            return features

        @app.route('/get-user-details')
        def get_user_details():
            user_details = MainTool.get_current_user_profile()
            return user_details

        @app.route('/get-genres')
        def get_genres():
            genres = MainTool.get_genres()
            return genres

        @app.route('/get-browse-categories')
        def get_browse_categories():
            browse_categories = MainTool.get_several_browse_categories()
            return browse_categories

        @app.route('/get-user-saved-tracks')
        def get_user_saved_tracks():
            user_saved_tracks = MainTool.get_users_saved_tracks()
            return user_saved_tracks

        if __name__ == '__main__':
            app.run(debug=False, host='0.0.0.0')

class MainTool():
    logger = logging.getLogger('werkzeug')  # grabs underlying WSGI logger
    # handler = logging.FileHandler('test.log')  # creates handler for the log file
    # logger.addHandler(handler)  # adds handler to the werkzeug WSGI logger
    
    @classmethod
    def initialize_app(cls):
        url = Authorization.initialize_authorization_code()
        # url = Authorization.initialize_authorization_code(response_type='token')


    @classmethod
    def get_user_tracks(cls, type='tracks'):
        params = Authorization.get_auth_params()
        url = f'https://api.spotify.com/v1/me/top/{type}'
        headers = {
            'Authorization': 'Bearer' + ' ' + params['access_token']
        }
        r = requests.get(url=url, headers=headers)
        if '200' not in str(r):
            Authorization.get_refresh_token()
            r = requests.get(url=url, headers=headers)
        res = r.json()
        ids = ''
        for item in res['items']:
            ids += item['id'] + ','
        return res, ids

    @classmethod
    def get_several_browse_categories(cls):
        params = Authorization.get_auth_params()
        url = f'https://api.spotify.com/v1/browse/categories'
        headers = {
            'Authorization': 'Bearer' + ' ' + params['access_token']
        }
        r = requests.get(url=url, headers=headers)
        if '200' not in str(r):
            Authorization.get_refresh_token()
            r = requests.get(url=url, headers=headers)
        res = r.json()
        return res

    @classmethod
    def get_genres(cls):
        params = Authorization.get_auth_params()
        url = f'https://api.spotify.com/v1/recommendations/available-genre-seeds'
        headers = {
            'Authorization': 'Bearer' + ' ' + params['access_token']
        }
        r = requests.get(url=url, headers=headers)
        if '200' not in str(r):
            Authorization.get_refresh_token()
            r = requests.get(url=url, headers=headers)
        res = r.json()
        return res

    @classmethod
    def get_users_saved_tracks(cls):
        params = Authorization.get_auth_params()
        url = f'https://api.spotify.com/v1/me/tracks'
        headers = {
            'Authorization': 'Bearer' + ' ' + params['access_token']
        }
        r = requests.get(url=url, headers=headers)
        if '200' not in str(r):
            Authorization.get_refresh_token()
            r = requests.get(url=url, headers=headers)
        res = r.json()
        return res

    @classmethod
    def get_tracks_audio_features(cls, id=None, ids=None):
        params = Authorization.get_auth_params()
        if ids:
            url = f'https://api.spotify.com/v1/audio-features?ids={ids}'
        if id:
            url = f'https://api.spotify.com/v1/audio-features/{id}'
        headers = {
            'Authorization': 'Bearer' + ' ' + params['access_token']
        }
        r = requests.get(url=url, headers=headers)
        if '200' not in str(r):
            Authorization.get_refresh_token()
            r = requests.get(url=url, headers=headers)
        res = r.json()
        return res

    @classmethod
    def get_current_user_profile(cls):
        params = Authorization.get_auth_params()
        url = f'https://api.spotify.com/v1/me'
        headers = {
            'Authorization': 'Bearer' + ' ' + params['access_token']
        }
        r = requests.get(url=url, headers=headers)
        if '200' not in str(r):
            Authorization.get_refresh_token()
            r = requests.get(url=url, headers=headers)
        res = r.json()
        return res


res = MainTool.initialize_app()
