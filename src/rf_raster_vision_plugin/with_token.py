from .http.raster_foundry import get_api_token


class WithRefreshToken(object):
    def set_token(self, rf_api_host: str, refresh_token: str):
        self.refresh_token = refresh_token
        self._token = get_api_token(refresh_token, rf_api_host)
