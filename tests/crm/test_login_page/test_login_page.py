from Page.crm import LoginPage


def test_login(data):
    page = LoginPage()
    page.login(data['email'], data['password'], data['code'])

    page.verify(*data['expect'])
