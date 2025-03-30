from django.contrib.auth.models import User, Group
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

class MySeleniumTests(StaticLiveServerTestCase):
    # no crearem una BD de test en aquesta ocasió (comentem la línia)
    #fixtures = ['testdb.json',]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opts = Options()
        cls.selenium = webdriver.Firefox(options=opts)  # Canviat de Chrome a Firefox
        cls.selenium.implicitly_wait(5)
        
        # Creem el superusuari
        user = User.objects.create_user("isard", "isard@isardvdi.com", "pirineus")
        user.is_superuser = True
        user.is_staff = True
        user.save()

        # Creem els grups 'profe' i 'alumne'
        group_profe = Group.objects.create(name='profe')
        group_alumne = Group.objects.create(name='alumne')

        # Creem un usuari per al grup 'profe' i l'afegim al grup
        profe_user = User.objects.create_user("profe", "profe@isardvdi.com", "password")
        profe_user.is_staff = True  # Assignem permís de 'staff'
        profe_user.save()
        profe_user.groups.add(group_profe)

        # Creem un usuari per al grup 'alumne' i l'afegim al grup
        alumne_user = User.objects.create_user("alumne", "alumne@isardvdi.com", "password")
        alumne_user.save()
        alumne_user.groups.add(group_alumne)

    def test_profe_can_access_admin(self):
        # Comprovem que l'usuari 'profe' pot accedir al panell d'administració
        
        # Accedeix a la pàgina de login
        self.selenium.get(f'{self.live_server_url}/admin/login/')
        
        # Esperem que carregui la pàgina de login
        time.sleep(2)

        # Trobar els camps de login
        username_field = self.selenium.find_element(By.NAME, "username")
        password_field = self.selenium.find_element(By.NAME, "password")

        # Rellenar les dades de login per a l'usuari 'profe'
        username_field.send_keys("profe")
        password_field.send_keys("password")

        # Enviar el formulari
        password_field.send_keys(Keys.RETURN)
        
        # Esperem que carregui el panell d'administració
        time.sleep(3)

        # Comprovem que l'usuari 'profe' ha accedit correctament
        self.assertIn("Log in | Django site admin", self.selenium.title)  # El títol serà aquest després de login

    def test_alumne_cannot_access_admin(self):
        # Comprovem que l'usuari 'alumne' no pot accedir al panell d'administració
        
        # Accedeix a la pàgina de login
        self.selenium.get(f'{self.live_server_url}/admin/login/')
        
        # Esperem que carregui la pàgina de login
        time.sleep(2)

        # Trobar els camps de login
        username_field = self.selenium.find_element(By.NAME, "username")
        password_field = self.selenium.find_element(By.NAME, "password")

        # Rellenar les dades de login per a l'usuari 'alumne'
        username_field.send_keys("alumne")
        password_field.send_keys("password")

        # Enviar el formulari
        password_field.send_keys(Keys.RETURN)
        
        # Esperem que es redirigeixi a la pàgina de login si no pot accedir
        time.sleep(3)

        # Comprovem que l'usuari 'alumne' ha estat redirigit a la pàgina de login
        self.assertIn("Log in | Django site admin", self.selenium.title)  # Títol de la pàgina de login

    @classmethod
    def tearDownClass(cls):
        # Tancar el navegador després de les proves
        cls.selenium.quit()
        super().tearDownClass()
