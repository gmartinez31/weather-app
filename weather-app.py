
import os
import tornado.ioloop
import tornado.web
import tornado.log
import requests

from dotenv import load_dotenv
from jinja2 import \
  Environment, PackageLoader, select_autoescape

load_dotenv('.env')

ENV = Environment(
  loader=PackageLoader('weather', 'templates'),
  autoescape=select_autoescape(['html', 'xml'])
)

class TemplateHandler(tornado.web.RequestHandler):
  def render_template (self, tpl, context):
    template = ENV.get_template(tpl)
    self.write(template.render(**context))
    
class MainHandler(TemplateHandler):
  def get (self):
    self.set_header(
      'Cache-Control',
      'no-store, no-cache, must-revalidate, max-age=0')
    self.render_template("home.html", {})
    
  def post (self):
    ### get city name###
    city = self.get_body_argument('city')

    ### lookup the weather###
    # this is a get request where we used a dictionary and having that as a parameter.
    # inside the dictionary we query the city variable, which is the requested city input by the user in our form in html.
    # the second part of the dictionary is simply our APPID which is loaded from the .env file.
    # the final line executes the get request with the url, query city, and our API ID (which is needed for the website we used)
    weather_req = {'q': city, 'units': 'imperial', 'APPID': os.environ['APPID']}
    r = requests.get('http://api.openweathermap.org/data/2.5/find', params=weather_req)
    
    ### render the weather data###
    data = r.json()
    city_name = data["list"][0]['name']
    temperature = data["list"][0]["main"]["temp"]
    wind = data["list"][0]["wind"]["speed"]
    # print(r.url)
    # r = requests.post('http://api.openweathermap.org/data/2.5/find', data=weather_req)
    return self.render_template("forecast.html", {'city_name': city_name, 'temperature': temperature, 'wind': wind})

class ForecastHandler(TemplateHandler):
  def get (self):
    self.set_header(
      'Cache-Control',
      'no-store, no-cache, must-revalidate, max-age=0')
    self.render_template("forecast.html", {})
    
def make_app():
  return tornado.web.Application([
    (r"/", MainHandler),
    (r"/forecast", ForecastHandler),
    (r"/static/(.*)", 
      tornado.web.StaticFileHandler, {'path': 'static'}),
  ], autoreload=True)
  
if __name__ == "__main__":
  tornado.log.enable_pretty_logging()
  app = make_app()
  app.listen(int(os.environ.get('PORT', '8080')))
  tornado.ioloop.IOLoop.current().start()