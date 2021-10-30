from PageObject.ctrip import LoginPage


def test_login(driver, data):
    page = LoginPage(driver)
    page.login(data['username'], data['password'])

    page.verify(*data['verification'])
