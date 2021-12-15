import requests
from bs4 import BeautifulSoup
import mysql.connector

search = input("Enter the name of the movie to extract its details from IMDb and dump into MySQL table: ")

url = "https://www.imdb.com/find?q=" + search.replace(" ","+") # URL of search results on IMDb
p = requests.get(url)
soup = BeautifulSoup(p.content, "html.parser")

try:
  movie = soup.tr.contents[3] # This is the first search result on results page of IMDb.
except:
  print('No such movie found.')
  quit()

if movie.a.string.lower() != search.lower():
  confirm = input('Did you mean %s? [y/n]: '%movie.a.string).lower()
  if confirm == 'n':
    print('We could not find the movie you entered.')
    quit()
  else:
    if confirm != 'y':
      print('Invalid response.')
      quit()
url = "https://www.imdb.com" + movie.a['href'] # This is the webpage of the searched movie on IMDb.


p = requests.get(url)
soup = BeautifulSoup(p.content, "html.parser")
scripts = [script for script in soup.find_all('script', type=="application/ld+json")]
details = eval(scripts[19].string) # This is the JSON on IMDb source code containing the details of the searched movie.

# Extracting important details about the movie from the JSON:
try:
  name = details['name']
  rating = float(details['aggregateRating']['ratingValue'])
  certificate = details['contentRating']

  genres = ''
  for genre in details['genre']:
    genres = genres + genre + '  '
  genres = genres.strip().replace('  ',', ')

  actors = ''
  for actor in details['actor']:
    actors = actors + actor['name'] + '  '
  actors = actors.strip().replace('  ',', ')

  directors = ''
  for director in details['director']:
    directors = directors + director['name'] + '  '
  directors = directors.strip().replace('  ',', ')

except:
  print('Alas! It is not a movie.')
  quit()

# Connecting to MySQL:
try:
  connection = mysql.connector.connect(user='root', password='',
                              host='localhost',
                             auth_plugin = 'mysql_native_password'
                              )
except:
  print('Connection to MySQL failed!')
  quit()

cmd = connection.cursor()

cmd.execute('CREATE DATABASE IF NOT EXISTS IMDb;') # Creates IMDb database on the first run of the script

cmd.execute('USE IMDb;')
cmd.execute('''CREATE TABLE IF NOT EXISTS Movies (
      Name varchar(255),
      Rating decimal(3,1),
      Certificate varchar(255),
      Genres varchar(255),
      Actors varchar(255),
      Directors varchar(255)
      );''') # Creates Movies table in IMDb database on the first run of the script

# Dumping the details extracted from IMDb about the movie in MySQL table:
cmd.execute("INSERT INTO Movies (name,rating,certificate,genres,actors,directors) VALUES ('%s',%s,'%s','%s','%s','%s');"%(name,rating,certificate,genres,actors,directors))
print("Details of %s was dumped into MySQL table."%movie.a.string)

cmd.close()
connection.commit()
connection.close()
