from Page.ctrip import LoginPage


def test_login(data):
    page = LoginPage()
    page.login(data['username'], data['password'])

    page.verify(*data['verification'])
