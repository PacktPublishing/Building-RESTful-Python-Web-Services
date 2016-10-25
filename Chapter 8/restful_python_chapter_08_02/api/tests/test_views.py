"""
Book: Building RESTful Python Web Services
Chapter 8: Testing and Ddeploying an API with Flask
Author: Gaston C. Hillar - Twitter.com/gastonhillar
Publisher: Packt Publishing Ltd. - http://www.packtpub.com
"""
from app import create_app
from base64 import b64encode
from flask import current_app, json, url_for
from models import db, Category, Message, User
import status
from unittest import TestCase


class InitialTests(TestCase):
    def setUp(self):
        self.app = create_app('test_config')
        self.test_client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.test_user_name = 'testuser'
        self.test_user_password = 'T3s!p4s5w0RDd12#'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_accept_content_type_headers(self):
        return {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def get_authentication_headers(self, username, password):
        authentication_headers = self.get_accept_content_type_headers()
        authentication_headers['Authorization'] = \
            'Basic ' + b64encode((username + ':' + password).encode('utf-8')).decode('utf-8')
        return authentication_headers

    def test_request_without_authentication(self):
        """
        Ensure we cannot access a resource that requirest authentication without an appropriate authentication header
        """
        response = self.test_client.get(
            url_for('api.messagelistresource', _external=True),
            headers=self.get_accept_content_type_headers())
        self.assertTrue(response.status_code == status.HTTP_401_UNAUTHORIZED)

    def create_user(self, name, password):
        url = url_for('api.userlistresource', _external=True)
        data = {'name': name, 'password': password}
        response = self.test_client.post(
            url, 
            headers=self.get_accept_content_type_headers(),
            data=json.dumps(data))
        return response

    def create_category(self, name):
        url = url_for('api.categorylistresource', _external=True)
        data = {'name': name}
        response = self.test_client.post(
            url, 
            headers=self.get_authentication_headers(self.test_user_name, self.test_user_password),
            data=json.dumps(data))
        return response

    def test_create_and_retrieve_category(self):
        """
        Ensure we can create a new Category and then retrieve it
        """
        create_user_response = self.create_user(self.test_user_name, self.test_user_password)
        self.assertEqual(create_user_response.status_code, status.HTTP_201_CREATED)
        new_category_name = 'New Information'
        post_response = self.create_category(new_category_name)
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.query.count(), 1)
        post_response_data = json.loads(post_response.get_data(as_text=True))
        self.assertEqual(post_response_data['name'], new_category_name)
        new_category_url = post_response_data['url']
        get_response = self.test_client.get(
            new_category_url,
            headers=self.get_authentication_headers(self.test_user_name, self.test_user_password))
        get_response_data = json.loads(get_response.get_data(as_text=True))
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response_data['name'], new_category_name)

    def test_create_duplicated_category(self):
        """
        Ensure we cannot create a duplicated Category
        """
        create_user_response = self.create_user(self.test_user_name, self.test_user_password)
        self.assertEqual(create_user_response.status_code, status.HTTP_201_CREATED)
        new_category_name = 'New Information'
        post_response = self.create_category(new_category_name)
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.query.count(), 1)
        post_response_data = json.loads(post_response.get_data(as_text=True))
        self.assertEqual(post_response_data['name'], new_category_name)
        second_post_response = self.create_category(new_category_name)
        self.assertEqual(second_post_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Category.query.count(), 1)

    def test_retrieve_categories_list(self):
        """
        Ensure we can retrieve the categories list
        """
        create_user_response = self.create_user(self.test_user_name, self.test_user_password)
        self.assertEqual(create_user_response.status_code, status.HTTP_201_CREATED)
        new_category_name_1 = 'Error'
        post_response_1 = self.create_category(new_category_name_1)
        self.assertEqual(post_response_1.status_code, status.HTTP_201_CREATED)
        new_category_name_2 = 'Warning'
        post_response_2 = self.create_category(new_category_name_2)
        self.assertEqual(post_response_2.status_code, status.HTTP_201_CREATED)
        url = url_for('api.categorylistresource', _external=True)
        get_response = self.test_client.get(
            url,
            headers=self.get_authentication_headers(self.test_user_name, self.test_user_password))
        get_response_data = json.loads(get_response.get_data(as_text=True))
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(get_response_data), 2)
        self.assertEqual(get_response_data[0]['name'], new_category_name_1)
        self.assertEqual(get_response_data[1]['name'], new_category_name_2)

    def test_update_category(self):
        """
        Ensure we can update the name for an existing category
        """
        create_user_response = self.create_user(self.test_user_name, self.test_user_password)
        self.assertEqual(create_user_response.status_code, status.HTTP_201_CREATED)
        new_category_name_1 = 'Error 1'
        post_response_1 = self.create_category(new_category_name_1)
        self.assertEqual(post_response_1.status_code, status.HTTP_201_CREATED)
        post_response_data_1 = json.loads(post_response_1.get_data(as_text=True))
        new_category_url = post_response_data_1['url']
        new_category_name_2 = 'Error 2'
        data = {'name': new_category_name_2}
        patch_response = self.test_client.patch(
            new_category_url, 
            headers=self.get_authentication_headers(self.test_user_name, self.test_user_password),
            data=json.dumps(data))
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        get_response = self.test_client.get(
            new_category_url,
            headers=self.get_authentication_headers(self.test_user_name, self.test_user_password))
        get_response_data = json.loads(get_response.get_data(as_text=True))
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response_data['name'], new_category_name_2)

    def create_message(self, message, duration, category):
        url = url_for('api.messagelistresource', _external=True)
        data = {'message': message, 'duration': duration, 'category': category}
        response = self.test_client.post(
            url, 
            headers=self.get_authentication_headers(self.test_user_name, self.test_user_password),
            data=json.dumps(data))
        return response

    def test_create_and_retrieve_message(self):
        """
        Ensure we can create a new message and then retrieve it
        """
        create_user_response = self.create_user(self.test_user_name, self.test_user_password)
        self.assertEqual(create_user_response.status_code, status.HTTP_201_CREATED)
        new_message_message = 'Welcome to the IoT world'
        new_message_category = 'Information'
        post_response = self.create_message(new_message_message, 15, new_message_category)
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.query.count(), 1)
        # The message should have created a new catagory
        self.assertEqual(Category.query.count(), 1)
        post_response_data = json.loads(post_response.get_data(as_text=True))
        self.assertEqual(post_response_data['message'], new_message_message)
        new_message_url = post_response_data['url']
        get_response = self.test_client.get(
            new_message_url,
            headers=self.get_authentication_headers(self.test_user_name, self.test_user_password))
        get_response_data = json.loads(get_response.get_data(as_text=True))
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response_data['message'], new_message_message)
        self.assertEqual(get_response_data['category']['name'], new_message_category)

    def test_create_duplicated_message(self):
        """
        Ensure we cannot create a duplicated Message
        """
        create_user_response = self.create_user(self.test_user_name, self.test_user_password)
        self.assertEqual(create_user_response.status_code, status.HTTP_201_CREATED)
        new_message_message = 'Welcome to the IoT world'
        new_message_category = 'Information'
        post_response = self.create_message(new_message_message, 15, new_message_category)
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.query.count(), 1)
        post_response_data = json.loads(post_response.get_data(as_text=True))
        self.assertEqual(post_response_data['message'], new_message_message)
        new_message_url = post_response_data['url']
        get_response = self.test_client.get(
            new_message_url,
            headers=self.get_authentication_headers(self.test_user_name, self.test_user_password))
        get_response_data = json.loads(get_response.get_data(as_text=True))
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response_data['message'], new_message_message)
        self.assertEqual(get_response_data['category']['name'], new_message_category)
        second_post_response = self.create_message(new_message_message, 15, new_message_category)
        self.assertEqual(second_post_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Message.query.count(), 1)

    def test_retrieve_messages_list(self):
        """
        Ensure we can retrieve the messages paginated list
        """
        create_user_response = self.create_user(self.test_user_name, self.test_user_password)
        self.assertEqual(create_user_response.status_code, status.HTTP_201_CREATED)
        new_message_message_1 = 'Welcome to the IoT world'
        new_message_category_1 = 'Information'
        post_response = self.create_message(new_message_message_1, 15, new_message_category_1)
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.query.count(), 1)
        new_message_message_2 = 'Initialization of the board failed'
        new_message_category_2 = 'Error'
        post_response = self.create_message(new_message_message_2, 10, new_message_category_2)
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.query.count(), 2)
        get_first_page_url = url_for('api.messagelistresource', _external=True)
        get_first_page_response = self.test_client.get(
            get_first_page_url,
            headers=self.get_authentication_headers(self.test_user_name, self.test_user_password))
        get_first_page_response_data = json.loads(get_first_page_response.get_data(as_text=True))
        self.assertEqual(get_first_page_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_first_page_response_data['count'], 2)
        self.assertIsNone(get_first_page_response_data['previous'])
        self.assertIsNone(get_first_page_response_data['next'])
        self.assertIsNotNone(get_first_page_response_data['results'])
        self.assertEqual(len(get_first_page_response_data['results']), 2)
        self.assertEqual(get_first_page_response_data['results'][0]['message'], new_message_message_1)
        self.assertEqual(get_first_page_response_data['results'][1]['message'], new_message_message_2)
        get_second_page_url = url_for('api.messagelistresource', page=2)
        get_second_page_response = self.test_client.get(
            get_second_page_url,
            headers=self.get_authentication_headers(self.test_user_name, self.test_user_password))
        get_second_page_response_data = json.loads(get_second_page_response.get_data(as_text=True))
        self.assertEqual(get_second_page_response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(get_second_page_response_data['previous'])
        self.assertEqual(get_second_page_response_data['previous'], url_for('api.messagelistresource', page=1))
        self.assertIsNone(get_second_page_response_data['next'])
        self.assertIsNotNone(get_second_page_response_data['results'])
        self.assertEqual(len(get_second_page_response_data['results']), 0)

    def test_update_message(self):
        """
        Ensure we can update a single field for an existing message
        """
        create_user_response = self.create_user(self.test_user_name, self.test_user_password)
        self.assertEqual(create_user_response.status_code, status.HTTP_201_CREATED)
        new_message_message_1 = 'Welcome to the IoT world'
        new_message_category_1 = 'Information'
        post_response = self.create_message(new_message_message_1, 30, new_message_category_1)
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.query.count(), 1)
        post_response_data = json.loads(post_response.get_data(as_text=True))
        new_message_url = post_response_data['url']
        new_printed_times = 1
        new_printed_once = True
        data = {'printed_times': new_printed_times, 'printed_once': new_printed_once}
        patch_response = self.test_client.patch(
            new_message_url, 
            headers=self.get_authentication_headers(self.test_user_name, self.test_user_password),
            data=json.dumps(data))
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        get_response = self.test_client.get(
            new_message_url,
            headers=self.get_authentication_headers(self.test_user_name, self.test_user_password))
        get_response_data = json.loads(get_response.get_data(as_text=True))
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response_data['printed_times'], new_printed_times)
        self.assertEqual(get_response_data['printed_once'], new_printed_once)
    
    def test_create_and_retrieve_user(self):
        """
        Ensure we can create a new User and then retrieve it
        """
        new_user_name = self.test_user_name
        new_user_password = self.test_user_password
        post_response = self.create_user(new_user_name, new_user_password)
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.query.count(), 1)
        post_response_data = json.loads(post_response.get_data(as_text=True))
        self.assertEqual(post_response_data['name'], new_user_name)
        new_user_url = post_response_data['url']
        get_response = self.test_client.get(
            new_user_url,
            headers=self.get_authentication_headers(self.test_user_name, self.test_user_password))
        get_response_data = json.loads(get_response.get_data(as_text=True))
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response_data['name'], new_user_name)
