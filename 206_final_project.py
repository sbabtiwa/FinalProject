#206 FINAL PROJECT OPTION 2 
#Sanika Babtiwale 

# Putting all import statements I need here.
import unittest
import collections 
import tweepy 
import twitter_info 
import json 
import sqlite3 
import itertools
import requests
import omdb
import re
from datetime import datetime


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

CACHE_FILE = "206_final_project_cache.json"
try:
	cached_data = open(CACHE_FILE, "r")
	file_contents = cached_data.read()
	cached_data.close()
	CACHE_DICT = json.loads(file_contents)

except: 
	CACHE_DICT = {}
	CACHE_DICT["MOVIE_DICT"] = {}
	CACHE_DICT["TWITTER_DICT"] = {}
	CACHE_DICT["USER_DICT"] = {}

#I will define a function called get_movie_info that caches movie data from OMDB. 
def get_movie_info(s):
	unique_key = "omdb_{}".format(s)
	if unique_key in CACHE_DICT["MOVIE_DICT"]: 
		print("Using cached omdb data for", s)
		pass 
	else: 
		print("Getting new data from omdb for", s)
		movie_data = omdb.get(title = s, fullplot = False, tomatoes = True)
		CACHE_DICT["MOVIE_DICT"][unique_key] = movie_data
		fileref = open(CACHE_FILE, "w")
		fileref.write(json.dumps(CACHE_DICT))
		fileref.close()		
	return CACHE_DICT["MOVIE_DICT"][unique_key]


#I will put the three movie title search terms in a list called omdb_movie_titles_list. 
omdb_movie_titles_list = ["Inside Out","Rogue One", "Fantastic Beasts and Where to Find Them"]


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
		return "The movie '{}' , IMDB id = {}, has been rated {} stars out of 10 on IMDB and can be found in {} language(s). One of the main actors in the movie is {}. The movie was released on {}.".format(self.movie_title, self.movie_id, self.movie_rating, self.num_languages(), self.top_billed_actor(), self.release_date_US)
	
	def tuple_of_data(self):
		movie_info_tuple = (self.movie_id, self.movie_title, self.movie_director, self.num_languages(), self.movie_rating, self.top_billed_actor(), self.release_date_US, self.runtime_in_min)
		return movie_info_tuple


#I will create a list called list_of_movie_instances that has instances of class Movie. 
list_of_movie_instances = []
for element in list_of_movie_dictionaries: 
	a_movie = Movie(element)
	list_of_movie_instances.append(a_movie)


#I will make a connection to a new database "finalproject.db". I will also create a variable to contain the database cursor. 
db_conn = sqlite3.connect("finalproject.db")
db_cur = db_conn.cursor()

#I will give instructions to drop the Movies table if it exists and create the table with the 8 column names and types of each. 
db_cur.execute("DROP TABLE IF EXISTS Movies")
db_cur.execute("CREATE TABLE Movies (movie_id TEXT PRIMARY KEY, movie_title TEXT, movie_director TEXT, num_languages INTEGER, movie_rating INTEGER, top_billed_actor TEXT, release_date_US TIMESTAMP, runtime_in_min TIMESTAMP)") 

#I will now insert the movie data into the Movies table using a for loop. 
insert_statement = "INSERT INTO Movies Values (?,?,?,?,?,?,?,?)"
for element in list_of_movie_instances: 
	db_cur.execute(insert_statement, element.tuple_of_data())

#I will use the database connection to commit the changes to the database. 
db_conn.commit()

# I will define a function called get_tweet_info that caches search term data from Twitter. 
def get_tweet_info(s): 
	unique_key = "twitter_{}".format(s)
	if unique_key in CACHE_DICT["TWITTER_DICT"]: 
		print("Using cached Twitter data for", s)
		pass 
	else: 
		print("Getting new data from Twitter for", s)
		tweet_data = api.search(q = s)
		tweets_about_movie = tweet_data["statuses"]
		CACHE_DICT["TWITTER_DICT"][unique_key] = tweets_about_movie
		fileref = open(CACHE_FILE, "w")
		fileref.write(json.dumps(CACHE_DICT))
		fileref.close()
	return CACHE_DICT["TWITTER_DICT"][unique_key]

# I will define a function called get_user_info that caches user info data from the Twitter search term data. 
def get_user_info(twitter_dict):

	list_of_all_users = []

	for x in twitter_dict:

		for element in x["entities"]["user_mentions"]:
			unique_key = "twitter_{}".format(element["screen_name"])
			if unique_key in CACHE_DICT["USER_DICT"]:
				print("Using cached user data for", element["screen_name"])
				pass 
			else:
				print("Getting new user data from web for", element["screen_name"])
				mention_user_id = element["id_str"]
				mention_user_screen_name = element["screen_name"]
				mention_user_info= api.get_user(element["screen_name"])
				CACHE_DICT["USER_DICT"][unique_key] = {}
				CACHE_DICT["USER_DICT"][unique_key]["id"] = mention_user_id
				CACHE_DICT["USER_DICT"][unique_key]["screen_name"] = mention_user_screen_name
				CACHE_DICT["USER_DICT"][unique_key]["favs"]= mention_user_info["favourites_count"]
				CACHE_DICT["USER_DICT"][unique_key]["description"] = mention_user_info["description"]
				CACHE_DICT["USER_DICT"][unique_key]["location"] = mention_user_info["location"]
				CACHE_DICT["USER_DICT"][unique_key]["language"] = mention_user_info["lang"]
				CACHE_DICT["USER_DICT"][unique_key]["followers"] = mention_user_info["followers_count"]
				fileref = open(CACHE_FILE, 'w')
				fileref.write(json.dumps(CACHE_DICT))
				fileref.close()

			list_of_all_users.append(CACHE_DICT["USER_DICT"][unique_key])

		unique_key = "twitter_{}".format(x["user"]["screen_name"])
		if unique_key in CACHE_DICT["USER_DICT"]: 
			print("Using cached user data for", x["user"]["screen_name"])
			pass 
		else:
			print("Getting new user data from web for", x["user"]["screen_name"])
			CACHE_DICT["USER_DICT"][unique_key] = {}
			CACHE_DICT["USER_DICT"][unique_key]["id"] = x["user"]["id_str"]
			CACHE_DICT["USER_DICT"][unique_key]["screen_name"] = x["user"]["screen_name"]
			CACHE_DICT["USER_DICT"][unique_key]["favs"] = x["user"]["favourites_count"]
			CACHE_DICT["USER_DICT"][unique_key]["description"] = x["user"]["description"]
			CACHE_DICT["USER_DICT"][unique_key]["location"] = x["user"]["location"]
			CACHE_DICT["USER_DICT"][unique_key]["language"] = x["user"]["lang"]
			CACHE_DICT["USER_DICT"][unique_key]["followers"] = x["user"]["followers_count"]
			fileref = open(CACHE_FILE, 'w')
			fileref.write(json.dumps(CACHE_DICT))
			fileref.close()

		list_of_all_users.append(CACHE_DICT["USER_DICT"][unique_key])

	return list_of_all_users

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


#I will create a list called list_of_actor_tweet_instances that holds Tweet instances of the top billed actor and movie id from each movie. I will also create a list called list_of_instances that holds invocations of the get_tweet_info function. 
list_of_actor_tweet_instances = []
list_of_instances = []
for a_movie in omdb_movie_titles_list:
	a_movie_actor = get_movie_actor(a_movie)
	a_movie_tweets = get_tweet_info(a_movie_actor)
	list_of_instances.append(a_movie_tweets)
	a_movie_id = get_movie_id(a_movie)
	for each_tweet in a_movie_tweets:
		an_instance = Tweet(each_tweet, a_movie_id)
		list_of_actor_tweet_instances.append(an_instance)

#I will give instructions to drop the Tweets table if it exists and create the table with the 6 column names and types of each. 
db_cur.execute("DROP TABLE IF EXISTS Tweets")
db_cur.execute("CREATE TABLE Tweets (tweet_id TEXT PRIMARY KEY, tweet_text TEXT, user_id TEXT, movie_id TEXT, num_favs INTEGER, num_retweets INTEGER, FOREIGN KEY (user_id) REFERENCES Users (user_id), FOREIGN KEY (movie_id) REFERENCES Movies (movie_id))") 

#I will now insert the tweet movie actor data into the Tweets table using a for loop.  
insert_tweet_statement = "INSERT OR IGNORE INTO Tweets Values (?,?,?,?,?,?)"
for element in list_of_actor_tweet_instances: 
	db_cur.execute(insert_tweet_statement, element.tuple_of_tweet_data())

#I will use the database connection to commit the changes to the database. 
db_conn.commit()


#I will invoke the get_user_info function on each tweet in the list_of_instances list and store them in a list called list_of_user_info.  
list_of_user_info = []
for y in list_of_instances: 
	user_info = get_user_info(y)
	list_of_user_info.append(user_info)

#I will define a class called TwitterUser that takes a dictionary with user information as input. 
class TwitterUser(object):
	def __init__(self, user_dict):
		self.users_id = user_dict["id"]
		self.users_screen_name = user_dict["screen_name"]
		self.users_favs = user_dict["favs"]
		self.users_description = user_dict["description"]
		self.users_location = user_dict["location"]
		self.users_language = user_dict["language"]
		self.users_followers  = user_dict["followers"]

	def __str__(self): 
		return "{} {} {}".format(self.users_id, self.users_screen_name, self.users_favs)

	def tuple_of_users_data(self): 
		users_tuple = (self.users_id, self.users_screen_name, self.users_favs, self.users_description, self.users_location, self.users_language, self.users_followers)
		return users_tuple

#I will create a list called list_user_instances that contains TwitterUser instances of each user in the list_of_user_info. 
list_user_instances = []
for each_element in list_of_user_info:
	for inside_user in each_element: 
		user_instance = TwitterUser(inside_user)
		list_user_instances.append(user_instance)


#I will give instructions to drop the Users table if it exists and create the table with the 7 column names and types of each. 
db_cur.execute("DROP TABLE IF EXISTS Users")
db_cur.execute("CREATE TABLE Users (user_id TEXT PRIMARY KEY, user_screen_name TEXT, user_favs INTEGER, user_description TEXT, user_location TEXT, user_language TEXT, user_followers INTEGER)") 

#I will insert the user info data into the Users table using a for loop. 
insert_user_statement = "INSERT OR IGNORE INTO Users Values (?,?,?,?,?,?,?)"
for element in list_user_instances:
	db_cur.execute(insert_user_statement, element.tuple_of_users_data())

#I will use the database connection to commit the changes to the database. 
db_conn.commit()

#I will make a query that finds the movie ids of tweets posted by English speaking users about a top billed actor in each movie, so I will be joining the Tweets table and Users table. I will use a counter to count the number of tweets per movie and save the resulting dictionary in a variable called dict_of_movies. The keys of the dictionary will be the movie id while the values are the number of tweets. 

q3 = "SELECT Tweets.movie_id FROM Tweets INNER JOIN Users ON Tweets.user_id = Users.user_id WHERE Users.user_language = 'en'"
db_cur.execute(q3)
all_movie_actors_tweeted_eng_users = db_cur.fetchall()
movie_actors_eng_users = [x[0] for x in all_movie_actors_tweeted_eng_users]
count_movies = collections.Counter()
for id_movie in movie_actors_eng_users: 
	count_movies[id_movie] += 1
dict_of_movies = dict(count_movies)
print (dict_of_movies)


#I will make a query that finds all the tweets about actress Amy Poehler from the movie Inside Out. Then, I will take the text and split the words. I will use regular expressions to find alphanumeric words and filter those words to find those that are longer than 5 characters. Finally, I will make a set comprehension and find the word with the longest length. 

q4 = "SELECT Tweets.tweet_text FROM Tweets INNER JOIN Movies ON Tweets.movie_id = Movies.movie_id WHERE Movies.movie_title = 'Inside Out'"
db_cur.execute(q4)
all_tweet_text_inside_out = db_cur.fetchall()
tweet_text_list = [text[0] for text in all_tweet_text_inside_out]

words_inside_out_tweets = []
for line in tweet_text_list: 
	the_words = line.split()
	for each_word in the_words:
		if re.match(r"^[a-zA-Z0-9]*$", each_word):
			words_inside_out_tweets.append(each_word)

list_of_long_words = list(filter(lambda x: len(x) > 5, words_inside_out_tweets))

set_of_long_words = {word for word in list_of_long_words}
longest_word_length = max(len(word) for word in set_of_long_words)


#I will make a query that finds all users' screen names and number of followers from the Users table who have favorites greater than 25. I will store the resulting tuples in a list called tuples_all_users. Then, I will sort the users by most number of followers to least and store the result in a variable called sorted_users. 

q5 = "SELECT user_screen_name, user_followers FROM Users WHERE user_favs > 25"
db_cur.execute(q5)
all_users_with_favs_greater_25 = db_cur.fetchall()
tuples_all_users = []
for each_tuple in all_users_with_favs_greater_25: 
	tuples_all_users.append(each_tuple)

sorted_users = sorted(tuples_all_users, key = lambda x: x[1], reverse = True)


#I will make a query that finds the movie title, id, and top billed actor from the Movies and store the result in a variable called movie_and_actor_tuples. I will use this query in my text file. 
q6 = "SELECT movie_title, movie_id, top_billed_actor FROM Movies"
db_cur.execute(q6)
movie_and_actor_tuples = db_cur.fetchall()


#I will write collected data to a "projectdata.txt" file. It will contain 3 movie titles, the movie ids, the data manipulation results, and the date of processing. 
file_object = open("projectdata.txt", "w")
file_object.write("Summary Stats for 206 Final Project Option 2" + "\n")
file_object.write("by Sanika Babtiwale" + "\n")
file_object.write("DATE OF PROCESSING: " + datetime.strftime(datetime.now(), '%Y/%m/%d') + "\n")
file_object.write("\n")
file_object.write("The top billed actors in three movies along with their OMDB IDs" + "\n")
file_object.write("\n")

file_object.write(("Name of Movie" + " " * 45)[:45] + ("OMDB ID" + " " * 15)[:15] + "Top Billed Actor" + "\n")
file_object.write(("-------------" + " " * 45)[:45] + ("-------" + " " * 15)[:15] + "----------------" + "\n")
for each_tuple in movie_and_actor_tuples:
	file_object.write(((str(each_tuple[0]) + " " * 45)[:45])+ ((str(each_tuple[1]) + " " * 15)[:15]) + str(each_tuple[2]) + "\n") 
file_object.write("\n")

file_object.write("Movie ids ordered by number of tweets about top billed actors from English speaking users" + "\n")
file_object.write("\n")
ordered_dict_of_movies = sorted(dict_of_movies.items(), key=lambda x: x[1])
print (ordered_dict_of_movies)
for each_tuple in ordered_dict_of_movies:
	file_object.write(str(each_tuple[0]) + ":" + " " + str(each_tuple[1]) + "\n")
file_object.write("\n")

file_object.write("The number of characters in the longest alphanumeric word in tweets that mentioned Amy Poehler" + "\n")
file_object.write("\n")
file_object.write("Alphanumeric characters in the longest word" + " = " + str(longest_word_length) + "\n")
file_object.write("\n")

file_object.write("The users having more than 25 favorites, ordered by the number of their followers in descending order" + "\n")
file_object.write("\n")
file_object.write(("Screen name" + " " * 20)[:20] + "Number of Followers" + "\n")
file_object.write(("-----------" + " " * 20)[:20] + "-------------------" + "\n")
for each_user in sorted_users: 
	file_object.write(((str(each_user[0] + " " * 20)[:20])) + str(each_user[1]) + "\n")
file_object.write("\n")
file_object.close()

# Tests for functions and class methods
class TestProject(unittest.TestCase):
	def test_movie_caching(self): 
		fname = open("206_final_project_cache.json", "r")
		filecon = fname.read()
		fname.close 
		self.assertTrue("Inside Out" in filecon) #testing whether movie data is in json file
	def test_get_OMDB_data(self): 
		movie_data = get_movie_info("Inside Out")
		self.assertEqual = (movie_data["title"], "Inside Out") #testing whether return value of function get_OMDB_data gives correct information 
	def test_Movie_string(self):
		movie = get_movie_info("Rogue One")
		movie_class = Movie(movie)
		self.assertEqual(type(movie_class.__str__()), type("")) #testing if __str__() method for Movie class returns a string
	def test_Movie_top_actor(self): 
		movie = get_movie_info("Fantastic Beasts and Where to Find Them")
		movie_class = Movie(movie)
		self.assertEqual(movie_class.top_billed_actor(), "Eddie Redmayne") #testing whether top_billed_actor method for Movie class returns correct value
	def test_Movie_num_languages(self): 
		movie = get_movie_info("Inside Out")
		movie_class = Movie(movie)
		self.assertEqual(movie_class.num_languages(), 1) #testing whether num_languages method for Movie class returns correct value
	def test_Movie_tuple(self): 
		movie = get_movie_info("Rogue One")
		movie_class = Movie(movie)
		self.assertEqual(type(movie_class.tuple_of_data()),tuple) #testing if tuple_of_data method for Movie class is correct type
	def test_tweet_info(self):
		movie_tweets = get_tweet_info("Felicity Jones")
		self.assertEqual(type(movie_tweets), type([])) #testing whether return value of function get_tweet_info is a list
	def test_tweet_info2(self):
		movie_tweets = get_tweet_info("Eddie Redmayne") 
		self.assertEqual(type(movie_tweets[0]), type({})) #testing if first element of function get_tweet_info is a dictionary
	def test_user_info(self): 
		movie_tweets = get_tweet_info("Amy Poehler")
		user_data = get_user_info(movie_tweets)
		self.assertEqual(type(user_data), type([])) #testing if return value of function get_user_info is a list
	def test_Tweet_str(self):
		actor_tweets = get_tweet_info("Eddie Redmayne")
		movie_id = get_movie_id("Fantastic Beasts and Where to Find Them")
		for each_tweet in actor_tweets: 
			tweet_string = Tweet(each_tweet, movie_id)
		self.assertEqual(type(tweet_string.__str__()), type("")) #testing that __str__ method of Tweet class returns a string
	def test_Tweet_tuple(self):
		actor_tweets = get_tweet_info("Felicity Jones")
		movie_id = get_movie_id("Rogue One")
		for each_tweet in actor_tweets:
			tweet_instance = Tweet(each_tweet, movie_id)
		self.assertEqual(type(tweet_instance.tuple_of_tweet_data()), tuple) #testing that tuple_of_tweet_data method of Tweet class returns correct type
	def test_get_movie_id(self): 
		one_movie_id = get_movie_id("Rogue One")
		self.assertEqual(one_movie_id, "tt3748528") #testing that get_movie_id function returns correct movie id for movie 
	def test_get_movie_actor(self): 
		movie_actor_name = get_movie_actor("Fantastic Beasts and Where to Find Them")
		self.assertEqual(movie_actor_name, "Eddie Redmayne") #testing that get_movie_actor function returns the correct actor name for movie
	def test_TwitterUser__str__(self):
		actor_tweets = get_tweet_info("Amy Poehler")
		user_information = get_user_info(actor_tweets)
		for each_user in user_information: 
			a_user = TwitterUser(each_user)
		self.assertEqual(type(a_user.__str__()), type("")) #testing that __str__ method of TwitterUser class returns correct type 
	def test_TwitterUser_tuple(self):
		actor_tweets = get_tweet_info("Felicity Jones")
		user_information = get_user_info(actor_tweets)
		for each_user in user_information: 
			a_user = TwitterUser(each_user)
		self.assertEqual(type(a_user.tuple_of_users_data()), tuple) #testing that tuple_of_users_data of TwitterUser class returns correct type
	

# Run main 
if __name__ == "__main__":
	unittest.main(verbosity=2)	

#Close the cursor to the database. 
db_conn.close()

