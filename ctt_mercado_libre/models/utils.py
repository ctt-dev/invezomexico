class MeliApi(object):

    AUTH_URL = "https://auth.mercadolibre.com.mx/authorization"

    host = "https://api.mercadolibre.com"

    client_id = ""
    client_secret = ""
    tg_code = ""
    access_token = ""
    refresh_token = ""
    redirect_uri = ""

    response = ""
    code = ""
    rjson = {}

    user = {}
    def __init__(self, client_id, client_secret, tg_code=None, access_token=None, refresh_token=None, redirect_uri=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.tg_code = tg_code
        self.access_token = access_token
        self.refresh_token = refresh_token