"""
Book: Building RESTful Python Web Services
Chapter 5: Developing RESTful APIs with Flask
Author: Gaston C. Hillar - Twitter.com/gastonhillar
Publisher: Packt Publishing Ltd. - http://www.packtpub.com
"""
class MessageModel:
    def __init__(self, message, duration, creation_date, message_category):
        # We will automatically generate the new id
        self.id = 0
        self.message = message
        self.duration = duration
        self.creation_date = creation_date
        self.message_category = message_category
        self.printed_times = 0
        self.printed_once = False
