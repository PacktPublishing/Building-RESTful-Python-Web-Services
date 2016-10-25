"""
Book: Building RESTful Python Web Services
Chapter 3: Improving and adding authentication to an API with Django
Author: Gaston C. Hillar - Twitter.com/gastonhillar
Publisher: Packt Publishing Ltd. - http://www.packtpub.com
"""
from django.contrib.auth.models import User
user = User.objects.create_user('kevin', 'kevin@example.com', 'kevinpassword') 

user.save()  
