import os
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth import get_user_model
from django.core.files import File
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.expected_conditions import invisibility_of_element_located
from selenium.webdriver.support.wait import WebDriverWait
from image_uploader_widget_demo.demo_application import models

User = get_user_model()

class ImageUploaderWidget(StaticLiveServerTestCase):
    admin_add_url = '/admin/demo_application/testnonrequired/add/'

    def get_url(self, path):
        return "%s%s" % (self.live_server_url, path)

    def get_edit_url(self, id):
        return "%s/admin/demo_application/testnonrequired/%s/change/" % (self.live_server_url, id)

    @property
    def image_file(self):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        mocks_dir = os.path.join(base_dir, "mocks")
        image = os.path.join(mocks_dir, "image.png")
        return image

    def setUp(self):
        self.user = User.objects.create_superuser(
            'admin', 'admin@admin.com', 'admin'
        )
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        self.selenium = webdriver.Chrome(options=chrome_options)
        self.selenium.get(self.get_url('/admin/login'))
        
        username = self.selenium.find_element(By.ID, "id_username")
        password = self.selenium.find_element(By.ID, "id_password")
        submit = self.selenium.find_element(By.XPATH, "//input[@type='submit']")

        username.send_keys('admin')
        password.send_keys('admin')
        submit.click()

    def test_empty_marker_click(self):
        """
        The empty marker must be visible and the file input click event should be
        called when click on the empty marker.
        """
        self.selenium.get(self.get_url(self.admin_add_url))

        form_row = self.selenium.find_element(By.CSS_SELECTOR, '.form-row.field-image')

        injected_javascript = (
            'const callback = arguments[0];'
            'const input = document.querySelector(".form-row.field-image input[type=file]");'
            'input.addEventListener("click", (e) => { e.preventDefault(); alert("CLICKED"); });'
            'callback();'
        )
        self.selenium.execute_async_script(injected_javascript)

        empty_marker = form_row.find_element(By.CSS_SELECTOR, '.iuw-empty')
        self.assertTrue(empty_marker.is_displayed())

        empty_marker.click()
        self.selenium.switch_to.alert.accept()
        
    def test_non_required_file_input(self):
        """
        When send an image to the file input, should render an preview image with img tag,
        preview button and remove button.
        """
        itens = models.TestNonRequired.objects.all()
        self.assertEqual(len(itens), 0)

        self.selenium.get(self.get_url(self.admin_add_url))

        form_row = self.selenium.find_element(By.CSS_SELECTOR, '.form-row.field-image')

        previews = form_row.find_elements(By.CSS_SELECTOR, '.iuw-image-preview')
        self.assertEqual(len(previews), 0)

        file_input = form_row.find_element(By.CSS_SELECTOR, 'input[type=file]')

        self.assertEqual(file_input.get_attribute('value'), "")

        file_input.send_keys(self.image_file)

        self.assertEqual(file_input.get_attribute('value'), "C:\\fakepath\\image.png")

        previews = form_row.find_elements(By.CSS_SELECTOR, '.iuw-image-preview')
        self.assertEqual(len(previews), 1)
        
        preview = previews[0]
        img = preview.find_element(By.TAG_NAME, 'img')
        preview_button = preview.find_element(By.CSS_SELECTOR, '.iuw-preview-icon')
        delete_button = preview.find_element(By.CSS_SELECTOR, '.iuw-delete-icon')
        self.assertTrue(preview.is_displayed())
        self.assertIsNotNone(img)
        self.assertIsNotNone(preview_button)
        self.assertIsNotNone(delete_button)

        submit = self.selenium.find_element(By.CSS_SELECTOR, '#testnonrequired_form [type="submit"]')
        submit.click()

        alert = WebDriverWait(self.selenium, timeout=3).until(lambda d: d.find_element(By.CSS_SELECTOR, ".messagelist .success"))
        self.assertIsNotNone(alert)
        itens = models.TestNonRequired.objects.all()
        self.assertEqual(len(itens), 1)
        item = itens[0]
        self.assertIsNotNone(item.image)


    def test_remove_button_with_non_saved_image(self):
        itens = models.TestNonRequired.objects.all()
        self.assertEqual(len(itens), 0)
        
        self.selenium.get(self.get_url(self.admin_add_url))
        
        form_row = self.selenium.find_element(By.CSS_SELECTOR, '.form-row.field-image')
        file_input = form_row.find_element(By.CSS_SELECTOR, 'input[type=file]')
        
        self.assertEqual(file_input.get_attribute('value'), "")
        
        file_input.send_keys(self.image_file)

        self.assertEqual(file_input.get_attribute('value'), "C:\\fakepath\\image.png")

        previews = form_row.find_elements(By.CSS_SELECTOR, '.iuw-image-preview')
        self.assertEqual(len(previews), 1)
        
        preview = previews[0]
        delete_button = preview.find_element(By.CSS_SELECTOR, '.iuw-delete-icon')

        delete_button.click()

        previews = form_row.find_elements(By.CSS_SELECTOR, '.iuw-image-preview')
        
        self.assertEqual(file_input.get_attribute('value'), "")
        self.assertEqual(len(previews), 0)

    def test_image_with_database_data(self):
        image_file = self.image_file
        item = models.TestNonRequired()
        with open(image_file, 'rb') as f:
            item.image.save("image.png", File(f))
        item.save()

        self.selenium.get(self.get_edit_url(item.id))

        form_row = self.selenium.find_element(By.CSS_SELECTOR, '.form-row.field-image')
        root = form_row.find_element(By.CSS_SELECTOR, '.iuw-root')

        previews = form_row.find_elements(By.CSS_SELECTOR, '.iuw-image-preview')
        self.assertEqual(len(previews), 1)
        self.assertEqual(root.get_attribute("data-raw"), item.image.url)

        preview = previews[0]
        img = preview.find_element(By.TAG_NAME, 'img')
        preview_button = preview.find_element(By.CSS_SELECTOR, '.iuw-preview-icon')
        delete_button = preview.find_element(By.CSS_SELECTOR, '.iuw-delete-icon')
        self.assertTrue(preview.is_displayed())
        self.assertIsNotNone(img)
        self.assertTrue(item.image.url in img.get_attribute('src'))
        self.assertIsNotNone(preview_button)
        self.assertIsNotNone(delete_button)        

    def test_delete_saved_image(self):
        image_file = self.image_file
        item = models.TestNonRequired()
        with open(image_file, 'rb') as f:
            item.image.save("image.png", File(f))
        item.save()

        self.selenium.get(self.get_edit_url(item.id))

        form_row = self.selenium.find_element(By.CSS_SELECTOR, '.form-row.field-image')
        checkbox = form_row.find_element(By.CSS_SELECTOR, '[type=checkbox]')
        previews = form_row.find_elements(By.CSS_SELECTOR, '.iuw-image-preview')
        preview = previews[0]

        self.assertFalse(checkbox.is_selected())

        delete_button = preview.find_element(By.CSS_SELECTOR, '.iuw-delete-icon')

        delete_button.click()

        previews = form_row.find_elements(By.CSS_SELECTOR, '.iuw-image-preview')
        self.assertEqual(len(previews), 0)

        self.assertTrue(checkbox.is_selected())

        submit = self.selenium.find_element(By.CSS_SELECTOR, '#testnonrequired_form [type="submit"]')
        submit.click()

        itens = models.TestNonRequired.objects.all()
        self.assertEqual(len(itens), 1)
        item = itens[0]
        self.assertFalse(bool(item.image))

    def test_click_on_the_preview_image(self):
        self.selenium.get(self.get_url(self.admin_add_url))

        form_row = self.selenium.find_element(By.CSS_SELECTOR, '.form-row.field-image')
        previews = form_row.find_elements(By.CSS_SELECTOR, '.iuw-image-preview')
        file_input = form_row.find_element(By.CSS_SELECTOR, 'input[type=file]')
        file_input.send_keys(self.image_file)
        
        injected_javascript = (
            'const callback = arguments[0];'
            'const input = document.querySelector(".form-row.field-image input[type=file]");'
            'input.addEventListener("click", (e) => { e.preventDefault(); alert("CLICKED"); });'
            'callback();'
        )
        self.selenium.execute_async_script(injected_javascript)

        previews = form_row.find_elements(By.CSS_SELECTOR, '.iuw-image-preview')
        self.assertEqual(len(previews), 1)
        preview = previews[0]

        img = preview.find_element(By.TAG_NAME, 'img')
        img.click()
        
        self.selenium.switch_to.alert.accept()

    def test_click_on_the_preview_button(self):
        self.selenium.get(self.get_url(self.admin_add_url))

        form_row = self.selenium.find_element(By.CSS_SELECTOR, '.form-row.field-image')
        previews = form_row.find_elements(By.CSS_SELECTOR, '.iuw-image-preview')
        file_input = form_row.find_element(By.CSS_SELECTOR, 'input[type=file]')
        file_input.send_keys(self.image_file)
        
        previews = form_row.find_elements(By.CSS_SELECTOR, '.iuw-image-preview')
        self.assertEqual(len(previews), 1)
        preview = previews[0]

        preview_button = preview.find_element(By.CSS_SELECTOR, '.iuw-preview-icon')
        preview_button.click()
        
        preview_modal = WebDriverWait(self.selenium, timeout=3).until(lambda d: d.find_element(By.CSS_SELECTOR, "#iuw-modal-element.visible"))
        self.assertIsNotNone(preview_modal)
        self.assertEqual(preview_modal.get_attribute('class'), 'iuw-modal visible')

        img = preview_modal.find_element(By.TAG_NAME, 'img')
        self.assertIsNotNone(img)

    def test_click_on_the_preview_button_and_image_on_modal(self):
        self.selenium.get(self.get_url(self.admin_add_url))

        form_row = self.selenium.find_element(By.CSS_SELECTOR, '.form-row.field-image')
        previews = form_row.find_elements(By.CSS_SELECTOR, '.iuw-image-preview')
        file_input = form_row.find_element(By.CSS_SELECTOR, 'input[type=file]')
        file_input.send_keys(self.image_file)
        
        previews = form_row.find_elements(By.CSS_SELECTOR, '.iuw-image-preview')
        self.assertEqual(len(previews), 1)
        preview = previews[0]

        preview_button = preview.find_element(By.CSS_SELECTOR, '.iuw-preview-icon')
        preview_button.click()
        
        preview_modal = WebDriverWait(self.selenium, timeout=3).until(lambda d: d.find_element(By.CSS_SELECTOR, "#iuw-modal-element.visible"))

        img = preview_modal.find_element(By.TAG_NAME, 'img')
        img.click()

        self.selenium.implicitly_wait(0.5)

        self.assertEqual(preview_modal.get_attribute("class"), "iuw-modal visible")

    def test_click_on_the_preview_button_and_close_on_modal(self):
        self.selenium.get(self.get_url(self.admin_add_url))

        form_row = self.selenium.find_element(By.CSS_SELECTOR, '.form-row.field-image')
        previews = form_row.find_elements(By.CSS_SELECTOR, '.iuw-image-preview')
        file_input = form_row.find_element(By.CSS_SELECTOR, 'input[type=file]')
        file_input.send_keys(self.image_file)
        
        previews = form_row.find_elements(By.CSS_SELECTOR, '.iuw-image-preview')
        self.assertEqual(len(previews), 1)
        preview = previews[0]

        preview_button = preview.find_element(By.CSS_SELECTOR, '.iuw-preview-icon')
        preview_button.click()
        
        preview_modal = WebDriverWait(self.selenium, timeout=3).until(lambda d: d.find_element(By.CSS_SELECTOR, "#iuw-modal-element.visible"))
        
        close_button = preview_modal.find_element(By.CSS_SELECTOR, '.iuw-modal-close')
        close_button.click()

        WebDriverWait(self.selenium, timeout=3).until(invisibility_of_element_located((By.CSS_SELECTOR, "#iuw-modal-element")));
