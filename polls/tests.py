from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth.models import User, Group

class MySeleniumTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opts = Options()
        cls.selenium = WebDriver(options=opts)
        cls.selenium.implicitly_wait(5)
        cls.live_server_url = 'http://0.0.0.0:8000'  # Sobrescribimos la URL del servidor

        # Crear superusuario inicial
        admin_user = User.objects.create_user("isard", "isard@isardvdi.com", "pirineus")
        admin_user.is_superuser = True
        admin_user.is_staff = True
        admin_user.save()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_create_groups_and_users(self):
        # Acceder al admin login como el usuario "isard"
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/login/'))
        username_input = self.selenium.find_element(By.NAME, "username")
        username_input.send_keys('isard')
        password_input = self.selenium.find_element(By.NAME, "password")
        password_input.send_keys('pirineus')
        self.selenium.find_element(By.XPATH, '//input[@value="Log in"]').click()

        # Crear grupos "profe" y "alumne"
        self.selenium.find_element(By.LINK_TEXT, "Groups").click()
        existing_groups = self.selenium.page_source
        if "profe" not in existing_groups:
            self.selenium.find_element(By.LINK_TEXT, "ADD GROUP").click()
            group_name = self.selenium.find_element(By.NAME, "name")
            group_name.send_keys("profe")
            self.selenium.find_element(By.NAME, "_save").click()  # Guardar el grupo
        if "alumne" not in existing_groups:
            self.selenium.find_element(By.LINK_TEXT, "ADD GROUP").click()
            group_name = self.selenium.find_element(By.NAME, "name")
            group_name.send_keys("alumne")
            self.selenium.find_element(By.NAME, "_save").click()  # Guardar el grupo

        # Crear usuario "profe_user"
        self.selenium.find_element(By.LINK_TEXT, "Users").click()
        existing_users = self.selenium.page_source
        if "profe_user" not in existing_users:
            self.selenium.find_element(By.LINK_TEXT, "ADD USER").click()
            new_username = self.selenium.find_element(By.NAME, "username")
            new_password = self.selenium.find_element(By.NAME, "password1")
            confirm_password = self.selenium.find_element(By.NAME, "password2")

            new_username.send_keys("profe_user")
            new_password.send_keys("profe123")
            confirm_password.send_keys("profe123")
            self.selenium.find_element(By.NAME, "_save").click()

            # Editar el usuario para asignarlo al grupo "profe" y habilitar "is_staff"
            self.selenium.find_element(By.LINK_TEXT, "profe_user").click()
            self.selenium.find_element(By.XPATH, '//option[text()="profe"]').click()  # Asignar grupo
            is_staff_checkbox = self.selenium.find_element(By.NAME, "is_staff")
            if not is_staff_checkbox.is_selected():
                is_staff_checkbox.click()
            self.selenium.find_element(By.NAME, "_save").click()

        # Crear usuario "alumne_user"
        if "alumne_user" not in existing_users:
            self.selenium.find_element(By.LINK_TEXT, "ADD USER").click()
            new_username = self.selenium.find_element(By.NAME, "username")
            new_password = self.selenium.find_element(By.NAME, "password1")
            confirm_password = self.selenium.find_element(By.NAME, "password2")

            new_username.send_keys("alumne_user")
            new_password.send_keys("alumne123")
            confirm_password.send_keys("alumne123")
            self.selenium.find_element(By.NAME, "_save").click()

            # Editar el usuario para asignarlo al grupo "alumne" sin habilitar "is_staff"
            self.selenium.find_element(By.LINK_TEXT, "alumne_user").click()
            self.selenium.find_element(By.XPATH, '//option[text()="alumne"]').click()  # Asignar grupo
            is_staff_checkbox = self.selenium.find_element(By.NAME, "is_staff")
            if is_staff_checkbox.is_selected():
                is_staff_checkbox.click()
            self.selenium.find_element(By.NAME, "_save").click()

        # Cerrar sesión del administrador
        logout_form = WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.XPATH, '//form[@action="/admin/logout/"]')))
        logout_form.submit()  # Enviar
