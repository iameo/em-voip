from flask import url_for


class TestRoute:
    def test_swagger_home(self, client):
        resp = client.get('/')
        assert resp.status_code == 200
