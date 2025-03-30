from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
import time

class MySeleniumTests(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opts = Options()
        cls.selenium = webdriver.Firefox(options=opts)
        cls.selenium.implicitly_wait(5)

    def create_admin_user(self):
        """ Accedeix a /admin, fa login i crea l'usuari admin si no existeix """
        self.selenium.get(f"{self.live_server_url}/admin/login/")
        time.sleep(2)

        # Login com a superusuari
        self.selenium.find_element(By.NAME, "username").send_keys("isard")
        self.selenium.find_element(By.NAME, "password").send_keys("pirineus")
        self.selenium.find_element(By.NAME, "password").send_keys(Keys.RETURN)
        time.sleep(3)

    def create_group(self, group_name):
        """ Crea un grup nou a Django Admin """
        self.selenium.get(f"{self.live_server_url}/admin/auth/group/add/")
        time.sleep(2)

        group_input = self.selenium.find_element(By.NAME, "name")
        group_input.send_keys(group_name)
        group_input.send_keys(Keys.RETURN)
        time.sleep(3)

    def create_user(self, username, password, email, group=None, is_staff=False):
        """ Crea un usuari nou i l'assigna a un grup si cal """
        self.selenium.get(f"{self.live_server_url}/admin/auth/user/add/")
        time.sleep(2)

        self.selenium.find_element(By.NAME, "username").send_keys(username)
        self.selenium.find_element(By.NAME, "password1").send_keys(password)
        self.selenium.find_element(By.NAME, "password2").send_keys(password)
        self.selenium.find_element(By.NAME, "password2").send_keys(Keys.RETURN)
        time.sleep(2)

        if group or is_staff:
            # Habilitem permisos si cal
            self.selenium.find_element(By.LINK_TEXT, username).click()
            time.sleep(2)

            if is_staff:
                self.selenium.find_element(By.NAME, "is_staff").click()

            if group:
                group_select = self.selenium.find_element(By.NAME, "groups")
                group_select.send_keys(group)

            self.selenium.find_element(By.NAME, "_save").click()
            time.sleep(3)

    def test_create_users_and_groups(self):
        """ Crea els usuaris i grups necessaris """
        self.create_admin_user()
        self.create_group("profe")
        self.create_group("alumne")
        self.create_user("professor", "profe123", "professor@test.com", "profe", is_staff=True)
        self.create_user("alumne", "alumne123", "alumne@test.com", "alumne", is_staff=False)

    def test_profe_can_access_admin(self):
        """ Comprova que el professor pot accedir a l'admin """
        self.selenium.get(f"{self.live_server_url}/admin/login/")
        time.sleep(2)

        self.selenium.find_element(By.NAME, "username").send_keys("professor")
        self.selenium.find_element(By.NAME, "password").send_keys("profe123")
        self.selenium.find_element(By.NAME, "password").send_keys(Keys.RETURN)
        time.sleep(3)

        self.assertIn("Site administration", self.selenium.title)

    def test_alumne_cannot_access_admin(self):
        """ Comprova que l'alumne NO pot accedir a l'admin """
        self.selenium.get(f"{self.live_server_url}/admin/login/")
        time.sleep(2)

        self.selenium.find_element(By.NAME, "username").send_keys("alumne")
        self.selenium.find_element(By.NAME, "password").send_keys("alumne123")
        self.selenium.find_element(By.NAME, "password").send_keys(Keys.RETURN)
        time.sleep(3)

        self.assertIn("Log in | Django site admin", self.selenium.title)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()
