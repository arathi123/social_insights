from authomatic import Authomatic

from authomatic.providers import oauth2

# Facebook api workaround
oauth2.Facebook.user_info_url = 'https://graph.facebook.com/v2.6/me?fields=id,first_name,last_name,picture,email,gender,timezone,third_party_id,locale,age_range'

CONFIG = {
    'fb': {

        'class_': oauth2.Facebook,

        # Facebook is an AuthorizationProvider too.
        'consumer_key': '1073828176023572',
        'consumer_secret': 'ff39a48281ace87f85ccb3a4ea97641f',

        # But it is also an OAuth 2.0 provider and it needs scope.
        'scope': ['public_profile', 'email','user_friends' ],
        'id': 1
    }
}

authomatic = Authomatic(config=CONFIG, secret='some random secret string')
