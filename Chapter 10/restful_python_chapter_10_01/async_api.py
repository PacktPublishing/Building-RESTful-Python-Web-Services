"""
Book: Building RESTful Python Web Services
Chapter 10: Working with asynchronous code, testing and deploying an API with Tornado
Author: Gaston C. Hillar - Twitter.com/gastonhillar
Publisher: Packt Publishing Ltd. - http://www.packtpub.com
"""
import status
from datetime import date
from tornado import web, escape, ioloop, httpclient, gen
from concurrent.futures import ThreadPoolExecutor
from tornado.concurrent import run_on_executor
from drone import Altimeter, Drone, Hexacopter, LightEmittingDiode


thread_pool = ThreadPoolExecutor()
drone = Drone()


class AsyncHexacopterHandler(web.RequestHandler):
    SUPPORTED_METHODS = ("GET", "PATCH")
    HEXACOPTER_ID = 1
    _thread_pool = thread_pool

    @gen.coroutine
    def get(self, id):
        if int(id) is not self.__class__.HEXACOPTER_ID:
            self.set_status(status.HTTP_404_NOT_FOUND)
            self.finish()
            return
        print("I've started retrieving hexacopter's status")
        hexacopter_status = yield self.retrieve_hexacopter_status()
        print("I've finished retrieving hexacopter's status")
        response = { 
            'speed': hexacopter_status.motor_speed,
            'turned_on': hexacopter_status.turned_on,
            }
        self.set_status(status.HTTP_200_OK)
        self.write(response)
        self.finish()

    @run_on_executor(executor="_thread_pool")
    def retrieve_hexacopter_status(self):
        return drone.hexacopter.get_hexacopter_status()
    
    @gen.coroutine
    def patch(self, id):
        if int(id) is not self.__class__.HEXACOPTER_ID:
            self.set_status(status.HTTP_404_NOT_FOUND)
            self.finish()
            return
        request_data = escape.json_decode(self.request.body) 
        if ('motor_speed' not in request_data.keys()) or \
            (request_data['motor_speed'] is None):
            self.set_status(status.HTTP_400_BAD_REQUEST)
            self.finish()
            return
        try:
            motor_speed = int(request_data['motor_speed'])
            print("I've started setting the hexacopter's motor speed")
            hexacopter_status = yield self.set_hexacopter_motor_speed(motor_speed)
            print("I've finished setting the hexacopter's motor speed")
            response = { 
                'speed': hexacopter_status.motor_speed,
                'turned_on': hexacopter_status.turned_on,
                }
            self.set_status(status.HTTP_200_OK)
            self.write(response)
            self.finish()
        except ValueError as e:
            print("I've failed setting the hexacopter's motor speed")
            self.set_status(status.HTTP_400_BAD_REQUEST)
            response = {
                'error': e.args[0]
                }
            self.write(response)
            self.finish()
       
    @run_on_executor(executor="_thread_pool")
    def set_hexacopter_motor_speed(self, motor_speed):
        return drone.hexacopter.set_motor_speed(motor_speed)


class AsyncLedHandler(web.RequestHandler):
    SUPPORTED_METHODS = ("GET", "PATCH")
    _thread_pool = thread_pool

    @gen.coroutine
    def get(self, id):
        int_id = int(id)
        if int_id not in drone.leds.keys():
            self.set_status(status.HTTP_404_NOT_FOUND)
            self.finish()
            return
        led = drone.leds[int_id]
        print("I've started retrieving {0}'s status".format(led.description))
        brightness_level = yield self.retrieve_led_brightness_level(led)
        print("I've finished retrieving {0}'s status".format(led.description))
        response = {
            'id': led.identifier,
            'description': led.description,
            'brightness_level': brightness_level
            }
        self.set_status(status.HTTP_200_OK)
        self.write(response)
        self.finish()

    @run_on_executor(executor="_thread_pool")
    def retrieve_led_brightness_level(self, led):
        return led.get_brightness_level()
    
    @gen.coroutine
    def patch(self, id):
        int_id = int(id)
        if int_id not in drone.leds.keys():
            self.set_status(status.HTTP_404_NOT_FOUND)
            self.finish()
            return
        led = drone.leds[int_id]
        request_data = escape.json_decode(self.request.body) 
        if ('brightness_level' not in request_data.keys()) or \
            (request_data['brightness_level'] is None):
            self.set_status(status.HTTP_400_BAD_REQUEST)
            self.finish()
            return
        try:
            brightness_level = int(request_data['brightness_level'])
            print("I've started setting the {0}'s brightness level".format(led.description))
            yield self.set_led_brightness_level(led, brightness_level)
            print("I've finished setting the {0}'s brightness level".format(led.description))
            response = {
                'id': led.identifier,
                'description': led.description,
                'brightness_level': brightness_level
                }
            self.set_status(status.HTTP_200_OK)
            self.write(response)
            self.finish()
        except ValueError as e:
            print("I've failed setting the {0}'s brightness level".format(led.description))
            self.set_status(status.HTTP_400_BAD_REQUEST)
            response = {
                'error': e.args[0]
                }
            self.write(response)
            self.finish()
       
    @run_on_executor(executor="_thread_pool")
    def set_led_brightness_level(self, led, brightness_level):
        return led.set_brightness_level(brightness_level)


class AsyncAltimeterHandler(web.RequestHandler):
    SUPPORTED_METHODS = ("GET")
    ALTIMETER_ID = 1
    _thread_pool = thread_pool

    @gen.coroutine
    def get(self, id):
        if int(id) is not self.__class__.ALTIMETER_ID:
            self.set_status(status.HTTP_404_NOT_FOUND)
            self.finish()
            return
        print("I've started retrieving the altitude")
        altitude = yield self.retrieve_altitude()
        print("I've finished retrieving the altitude")
        response = { 
            'altitude': altitude
            }
        self.set_status(status.HTTP_200_OK)
        self.write(response)
        self.finish()

    @run_on_executor(executor="_thread_pool")
    def retrieve_altitude(self):
        return drone.altimeter.get_altitude()


application = web.Application([
    (r"/hexacopters/([0-9]+)", AsyncHexacopterHandler),
    (r"/leds/([0-9]+)", AsyncLedHandler),
    (r"/altimeters/([0-9]+)", AsyncAltimeterHandler),
],debug=True)


if __name__ == "__main__":
    port = 8888
    print("Listening at port {0}".format(port))
    application.listen(port)
    ioloop.IOLoop.instance().start()
