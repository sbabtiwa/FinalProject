###### INSTRUCTIONS ###### 

# An outline for preparing your final project assignment is in this file.

# Below, throughout this file, you should put comments that explain exactly what you should do for each step of your project. You should specify variable names and processes to use. For example, "Use dictionary accumulation with the list you just created to create a dictionary called tag_counts, where the keys represent tags on flickr photos and the values represent frequency of times those tags occur in the list."

# You can use second person ("You should...") or first person ("I will...") or whatever is comfortable for you, as long as you are clear about what should be done.

# Some parts of the code should already be filled in when you turn this in:
# - At least 1 function which gets and caches data from 1 of your data sources, and an invocation of each of those functions to show that they work 
# - Tests at the end of your file that accord with those instructions (will test that you completed those instructions correctly!)
# - Code that creates a database file and tables as your project plan explains, such that your program can be run over and over again without error and without duplicate rows in your tables.
# - At least enough code to load data into 1 of your dtabase tables (this should accord with your instructions/tests)

######### END INSTRUCTIONS #########

# Put all import statements you need here.
import unittest
import collections 
import tweepy 
import twitter_info 
import json 
import sqlite3 
import itertools
import requests
import omdb 

# Begin filling in instructions....

#Twitter authentication information from HW 5 
consumer_key = twitter_info.consumer_key
consumer_secret = twitter_info.consumer_secret
access_token = twitter_info.access_token
access_token_secret = twitter_info.access_token_secret
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

#Set up library to retrieve Twitter data with my authentication from HW 5 
api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())


#I will set up a try/except block where I will try to open the project JSON file and put the string contents in a dictionary. If there is no such file, I will create an empty dictionary and store it in a variable called CACHE_DICT. 

CACHE_FILE = "206_data_access_cache.json"
try: 
	cached_data = open(CACHE_FILE, "r")
	file_contents = cached_data.read()
	cached_data.close()
	CACHE_DICT = json.loads(file_contents)
except: 
	CACHE_DICT = {}

#I will define a function called get_movie_info that caches movie data from OMDB. 
def get_movie_info(s):
	unique_key = "omdb_{}".format(s)
	if unique_key in CACHE_DICT: 
		print("Using cached data for", s)
		pass 
	else: 
		print("Getting new data from omdb for", s)
		movie_data = omdb.get(title = s, fullplot = False, tomatoes = True)
		CACHE_DICT[unique_key] = movie_data
		fileref = open(CACHE_FILE, "w")
		fileref.write(json.dumps(CACHE_DICT))
		fileref.close()		
	return CACHE_DICT[unique_key]


#I will put the three movie title search terms in a list called omdb_movie_titles_list. 
omdb_movie_titles_list = ["Moana","The Hundred-Foot Journey", "Fantastic Beasts and Where to Find Them"]


#I will invoke the get_movie_info function on each of the three movie titles and store the return values in a list called list_of_movie_dictionaries. 
list_of_movie_dictionaries = []
for element in omdb_movie_titles_list:
	list_of_movie_dictionaries.append(get_movie_info(element))


#I will define a class called Movie that takes the dictionary with the movie's information as input to its constructor. 
class Movie(object):
	def __init__(self, movie_dict):
		self.movie_id = movie_dict["imdb_id"]
		self.movie_title = movie_dict["title"]
		self.movie_director = movie_dict["director"]
		self.movie_rating = movie_dict["imdb_rating"]
		self.release_date_US = movie_dict["released"]
		self.runtime_in_min = movie_dict["runtime"]
		self.movie_languages = movie_dict["language"]
		self.cast_list = movie_dict["actors"]

	def num_languages(self):
		return len(self.movie_languages.split())

	def top_billed_actor(self): 
		return self.cast_list.split(",") [0]

	def __str__(self):
		return "The movie '{}' , IMDB id = {}, has been rated {} stars out of 10 on IMDB and can be found in {} language(s). One of the main actors in the movie is {}.".format(self.movie_title, self.movie_id, self.movie_rating, self.num_languages(), self.top_billed_actor())
	
	def tuple_of_data(self):
		movie_info_tuple = (self.movie_id, self.movie_title, self.movie_director, self.num_languages(), self.movie_rating, self.top_billed_actor(), self.release_date_US, self.runtime_in_min)
		return movie_info_tuple


#I will create a list called list_of_movie_instances that has instances of class Movie. 
list_of_movie_instances = []
for element in list_of_movie_dictionaries: 
	a_movie = Movie(element) 
	list_of_movie_instances.append(a_movie)


#I will make a connection to a new database finalproject.db. I will also create a variable to contain the database cursor. 
db_conn = sqlite3.connect("finalproject.db")
db_cur = db_conn.cursor()

#I will give instructions to drop the Movies table if it exists and create the table with the 8 column names and types of each. 
db_cur.execute("DROP TABLE IF EXISTS Movies")
db_cur.execute("CREATE TABLE Movies (movie_id TEXT PRIMARY KEY, movie_title TEXT, movie_director TEXT, num_languages INTEGER, movie_rating INTEGER, top_billed_actor TEXT, release_date_US TIMESTAMP, runtime_in_min TIMESTAMP)") 

#I will now insert the movie data into the Movies table using a for loop. 
insert_statement = "INSERT INTO Movies Values (?,?,?,?,?,?,?,?)"
for element in list_of_movie_instances: 
	db_cur.execute(insert_statement, element.tuple_of_data())

db_conn.commit()

# I will define a function called get_tweet_info that caches search term data from Twitter. 
def get_tweet_info(s): 
	unique_key = "twitter_{}".format(s)
	if unique_key in CACHE_DICT: 
		print("Using cached data for", s)
		pass 
	else: 
		print("Getting new data from Twitter for", s)
		tweet_data = api.search(q = s)
		tweets_about_movie = tweet_data["statuses"]
		CACHE_DICT[unique_key] = tweets_about_movie
		fileref = open(CACHE_FILE, "w")
		fileref.write(json.dumps(CACHE_DICT))
		fileref.close()
	return CACHE_DICT[unique_key]

# I will define a function called get_user_info that caches user info data from the Twitter search term data. 
def get_user_info(twitter_dict):
	for x in twitter_dict:
		for element in x["entities"]["user_mentions"]:
			unique_key = "twitter_{}".format(element["screen_name"])
			if unique_key in CACHE_DICT:
				print("Using cached user data for", element["screen_name"])
				pass 
			else:
				print("Getting new user data from web for", element["screen_name"])
				user_favs = api.favorites(element["screen_name"])
				user_description = api.get_user(element["screen_name"])
				CACHE_DICT[unique_key] = {}
				CACHE_DICT[unique_key]["favs"]= user_favs
				CACHE_DICT[unique_key]["description"] = user_description["description"]
				fileref = open(CACHE_FILE, 'w')
				fileref.write(json.dumps(CACHE_DICT))
				fileref.close()
			if unique_key in CACHE_DICT: 
				print("Using cached user data for", x["user"]["screen_name"])
				pass 
			else:
				print("Getting new user data from web for", x["user"]["screen_name"])
				user_num_favs = api.favorites(x["user"]["screen_name"])
				CACHE_DICT[unique_key] = {}
				CACHE_DICT[unique_key]["favs"]= user_num_favs
				CACHE_DICT[unique_key]["description"] = x["user"]["description"]
				fileref = open(CACHE_FILE, 'w')
				fileref.write(json.dumps(CACHE_DICT))
				fileref.close()
	return CACHE_DICT[unique_key]

#I will define a class called Tweet that takes a dictionary with the search term's information as input to its constructor. 
class Tweet(object): 
	def __init__(self, twitter_dict, movie_id): 
		self.tweet_text = twitter_dict["text"]
		self.tweet_id = twitter_dict["id"]
		self.user_id = twitter_dict["user"]["id"]
		self.movie_id = movie_id
		self.num_favs = twitter_dict["favorite_count"]
		self.num_retweets = twitter_dict["retweet_count"]

	def __str__(self):
		return "{} {} {} {} {}".format(self.tweet_id, self.user_id, self.movie_id, self.num_favs, self.num_retweets)

	def tuple_of_tweet_data(self):
		tweet_tuple = (self.tweet_id, self.tweet_text, self.user_id, self.movie_id, self.num_favs, self.num_retweets)
		return tweet_tuple

#I will give instructions to drop the Tweets table if it exists and create the table with the 6 column names and types of each. 
db_cur.execute("DROP TABLE IF EXISTS Tweets")
db_cur.execute("CREATE TABLE Tweets (tweet_id TEXT PRIMARY KEY, tweet_text TEXT, user_id TEXT, movie_id TEXT, num_favs INTEGER, num_retweets INTEGER, FOREIGN KEY (movie_id) REFERENCES Movies (movie_id))") 

#I will define a function called get_movie_id that retrieves the movie's id from the Movies table. 
def get_movie_id(s):
	q1 = "SELECT movie_id FROM Movies WHERE movie_title = '{}' ".format(s)
	db_cur.execute(q1)
	movie_id_info = db_cur.fetchall()
	return movie_id_info[0][0]


#I will define a function called get_movie_actor that retrieves the movie's top billed actor from the Movies table. 
def get_movie_actor(s): 
	q2 = "SELECT top_billed_actor FROM Movies WHERE movie_title = '{}' ".format(s)
	db_cur.execute(q2)
	movie_actor_info = db_cur.fetchall()
	return movie_actor_info[0][0]


#I will create a list called list_of_actor_tweet_instances that holds Tweet instances of the top billed actor and movie id from each movie. 
list_of_actor_tweet_instances = []
for a_movie in omdb_movie_titles_list:
	a_movie_id = get_movie_id(a_movie)
	a_movie_actor = get_movie_actor(a_movie)
	a_movie_tweets = get_tweet_info(a_movie_actor)
	for each_tweet in a_movie_tweets:
		an_instance = Tweet(each_tweet, a_movie_id)
		list_of_actor_tweet_instances.append(an_instance)

#I will now insert the tweet movie actor data into the Tweets table using a for loop.  
insert_tweet_statement = "INSERT OR IGNORE INTO Tweets Values (?,?,?,?,?,?)"
for element in list_of_actor_tweet_instances: 
	db_cur.execute(insert_tweet_statement, element.tuple_of_tweet_data())

#I will use the database connection to commit the changes to the database. 
db_conn.commit()

#I will create a list called actor_list that holds get_tweet_info instances of each actor.
actor_list = ["Auli'i Cravalho", "Helen Mirren", "Eddie Redmayne"]
list_of_movie_info = []
for element in actor_list: 
	tweet_info = get_tweet_info(element)
	list_of_movie_info.append(tweet_info)

#I will invoke the get_user_info function on each Tweet instance and store them in a list called list_of_user_info.
list_of_user_info = []
for y in list_of_movie_info: 
	user_info = get_user_info(y)
	list_of_user_info.append(user_info)
#print(list_of_user_info)


# Put your tests here, with any edits you now need from when you turned them in with your project plan.
class TestProject(unittest.TestCase):
	def test_movie_caching(self): 
		fname = open("206_data_access_cache.json", "r")
		filecon = fname.read()
		fname.close 
		self.assertTrue("Moana" in filecon) #testing whether movie data is in json file
	def test_get_OMDB_data(self): 
		movie_data = get_movie_info("Moana")
		self.assertEqual = (movie_data, {"Title":"Moana","Year":"2016","Rated":"PG","Released":"23 Nov 2016","Runtime":"107 min","Genre":"Animation, Adventure, Comedy","Director":"Ron Clements, Don Hall, John Musker, Chris Williams","Writer":"Jared Bush (screenplay), Ron Clements (story by), John Musker (story by), Chris Williams (story by), Don Hall (story by), Pamela Ribon (story by), Aaron Kandell (story by), Jordan Kandell (story by)","Actors":"Auli'i Cravalho, Dwayne Johnson, Rachel House, Temuera Morrison","Plot":"In Ancient Polynesia, when a terrible curse incurred by the Demigod Maui reaches an impetuous Chieftain's daughter's island, she answers the Ocean's call to seek out the Demigod to set things right.","Language":"English","Country":"USA","Awards":"Nominated for 2 Oscars. Another 11 wins & 66 nominations.","Poster":"https://images-na.ssl-images-amazon.com/images/M/MV5BMjI4MzU5NTExNF5BMl5BanBnXkFtZTgwNzY1MTEwMDI@._V1_SX300.jpg","Ratings":[{"Source":"Internet Movie Database","Value":"7.7/10"},{"Source":"Rotten Tomatoes","Value":"95%"},{"Source":"Metacritic","Value":"81/100"}],"Metascore":"81","imdbRating":"7.7","imdbVotes":"93,475","imdbID":"tt3521164","Type":"movie","DVD":"07 Mar 2017","BoxOffice":"$248,558,024.00","Production":"Walt Disney Pictures","Website":"http://movies.disney.com/moana","Response":"True"}) #testing whether return value of function get_OMDB_data gives correct information 
	def test_tweet_info(self):
		movie_tweets = get_tweet_info("moana")
		self.assertEqual(type(movie_tweets), type([])) #testing whether return value of function get_tweet_info is a list
	def test_tweet_info2(self):
		movie_tweets = get_tweet_info("fantastic beasts") 
		self.assertEqual(type(movie_tweets[0]), type({})) #testing if first element of function get_tweet_info is a dictionary
	def test_user_info(self): 
		movie_tweets = get_tweet_info("hundred-foot journey")
		user_data = get_user_info(movie_tweets)
		self.assertEqual(type(user_data), type({})) #testing if return value of function get_user_info is a dictionary
	def test_Movie_string(self):
		movie = get_movie_info("Moana")
		movie_class = Movie(movie)
		self.assertEqual(type(movie_class.__str__()), type("")) #testing if __str__() method for Movie class returns a string
	def test_Movie_top_actor(self): 
		movie2 = get_movie_info("Fantastic Beasts and Where to Find Them")
		movie2_class = Movie(movie2)
		self.assertEqual(movie2_class.top_billed_actor(), "Eddie Redmayne") #testing whether top_billed_actor method for Movie class returns correct value
	def test_Movie_num_languages(self): 
		movie3 = get_movie_info("The Hundred-Foot Journey")
		movie3_class = Movie(movie3)
		self.assertEqual(movie3_class.num_languages(), 2) #testing whether num_languages method for Movie class returns correct value
	def test_get_movie_id(self): 
		one_movie_id = get_movie_id("The Hundred-Foot Journey")
		self.assertEqual(one_movie_id, "tt2980648") #testing that get_movie_id function returns correct movie id for movie 
	def test_get_movie_id2(self): 
		movie_id_value = get_movie_id("Moana")
		self.assertEqual(type(movie_id_value), type("")) #testing that get_movie_id function's return value is a string 
	def test_get_movie_actor(self): 
		movie_actor_name = get_movie_actor("Fantastic Beasts and Where to Find Them")
		self.assertEqual(movie_actor_name, "Eddie Redmayne") #testing that get_movie_actor function returns the correct actor name for movie 
	def test_twtable_columns(self):
		db_conn = sqlite3.connect("finalproject.db")
		db_cur = db_conn.cursor()
		db_cur.execute("SELECT * FROM Tweets")
		tweets = db_cur.fetchall()
		self.assertTrue(len(tweets[1]) == 6) #testing that there are 6 columns in the tweet table 
		db_conn.close()


# Remember to invoke your tests so they will run! (Recommend using the verbosity=2 argument.)
if __name__ == "__main__":
	unittest.main(verbosity=2)	

#I will close the cursor to the database. 
db_conn.close()

