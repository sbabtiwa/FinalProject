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
from itertools import filterfalse
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

CACHE_FILE = "206_final_project_cache.json"
try:
	cached_data = open(CACHE_FILE, "r")
	file_contents = cached_data.read()
	cached_data.close()
	CACHE_DICT = json.loads(file_contents)
	#for majorkey, subdict in CACHE_DICT.iteritems():
		#print (majorkey)
		#for subkey, value in subdict.iteritems():
			#print (subkey, value)
	#print(CACHE_DICT.keys())
	#print(CACHE_DICT["MOVIE_DICT"].keys())
	#print(CACHE_DICT["TWITTER_DICT"].keys())
	#print(CACHE_DICT["USER_DICT"].keys())

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
		return "The movie '{}' , IMDB id = {}, has been rated {} stars out of 10 on IMDB and can be found in {} language(s). One of the main actors in the movie is {}.".format(self.movie_title, self.movie_id, self.movie_rating, self.num_languages(), self.top_billed_actor())
	
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
				#list_of_all_users = []
				#list_of_all_users.append(CACHE_DICT[unique_key])
				pass 
			else:
				print("Getting new user data from web for", element["screen_name"])
				mention_user_id = element["id_str"]
				mention_user_screen_name = element["screen_name"]
				#user_favs = len(api.favorites(element["screen_name"]))
				mention_user_info= api.get_user(element["screen_name"])
				CACHE_DICT["USER_DICT"][unique_key] = {}
				CACHE_DICT["USER_DICT"][unique_key]["id"] = mention_user_id
				CACHE_DICT["USER_DICT"][unique_key]["screen_name"] = mention_user_screen_name
				CACHE_DICT["USER_DICT"][unique_key]["favs"]= mention_user_info["favourites_count"]
				CACHE_DICT["USER_DICT"][unique_key]["description"] = mention_user_info["description"]
				CACHE_DICT["USER_DICT"][unique_key]["location"] = mention_user_info["location"]
				CACHE_DICT["USER_DICT"][unique_key]["language"] = mention_user_info["lang"]
				CACHE_DICT["USER_DICT"][unique_key]["followers"] = mention_user_info["followers_count"]
				#list_of_all_users = []
				#list_of_all_users.append(CACHE_DICT[unique_key])
				fileref = open(CACHE_FILE, 'w')
				fileref.write(json.dumps(CACHE_DICT))
				fileref.close()

			list_of_all_users.append(CACHE_DICT["USER_DICT"][unique_key])
			#list_of_all_users.append(CACHE_DICT[unique_key]["id"])
			#list_of_all_users.append(CACHE_DICT[unique_key]["screen_name"])
			#list_of_all_users.append(CACHE_DICT[unique_key]["favs"])
			#list_of_all_users.append(CACHE_DICT[unique_key]["description"])
				#CACHE_DICT[unique_key]["favs"], CACHE_DICT[unique_key]["description"] ) 
			#for unique_key in CACHE_DICT: 
				#list_of_all_users.append(CACHE_DICT[unique_key])

		unique_key = "twitter_{}".format(x["user"]["screen_name"])
		if unique_key in CACHE_DICT["USER_DICT"]: 
			print("Using cached user data for", x["user"]["screen_name"])
			#list_of_all_users = []
			#list_of_all_users.append(CACHE_DICT[unique_key])
			pass 
		else:
			print("Getting new user data from web for", x["user"]["screen_name"])
			#a_user_id = x["user"]["id_str"]
			#user_num_favs = api.favorites(x["user"]["screen_name"])
			CACHE_DICT["USER_DICT"][unique_key] = {}
			CACHE_DICT["USER_DICT"][unique_key]["id"] = x["user"]["id_str"]
			CACHE_DICT["USER_DICT"][unique_key]["screen_name"] = x["user"]["screen_name"]
			CACHE_DICT["USER_DICT"][unique_key]["favs"] = x["user"]["favourites_count"]
			CACHE_DICT["USER_DICT"][unique_key]["description"] = x["user"]["description"]
			CACHE_DICT["USER_DICT"][unique_key]["location"] = x["user"]["location"]
			CACHE_DICT["USER_DICT"][unique_key]["language"] = x["user"]["lang"]
			CACHE_DICT["USER_DICT"][unique_key]["followers"] = x["user"]["followers_count"]
			#list_of_all_users = []
			#list_of_all_users.append(CACHE_DICT[unique_key])
			fileref = open(CACHE_FILE, 'w')
			fileref.write(json.dumps(CACHE_DICT))
			fileref.close()

		#list_of_all_users.append(CACHE_DICT["USER_DICT"][unique_key]["id"])
		#list_of_all_users.append(CACHE_DICT["USER_DICT"][unique_key]["screen_name"])
		#list_of_all_users.append(len(CACHE_DICT["USER_DICT"][unique_key]["favs"]))
		#list_of_all_users.append(CACHE_DICT["USER_DICT"][unique_key]["description"])
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

#I will give instructions to drop the Tweets table if it exists and create the table with the 6 column names and types of each. 
db_cur.execute("DROP TABLE IF EXISTS Tweets")
db_cur.execute("CREATE TABLE Tweets (tweet_id TEXT PRIMARY KEY, tweet_text TEXT, user_id TEXT, movie_id TEXT, num_favs INTEGER, num_retweets INTEGER, FOREIGN KEY (user_id) REFERENCES Users (user_id), FOREIGN KEY (movie_id) REFERENCES Movies (movie_id))") 


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
list_of_instances = []
for a_movie in omdb_movie_titles_list:
	a_movie_id = get_movie_id(a_movie)
	a_movie_actor = get_movie_actor(a_movie)
	a_movie_tweets = get_tweet_info(a_movie_actor)
	list_of_instances.append(a_movie_tweets)
	a_movie_id = get_movie_id(a_movie)
	for each_tweet in a_movie_tweets:
		an_instance = Tweet(each_tweet, a_movie_id)
		list_of_actor_tweet_instances.append(an_instance)
#print(list_of_instances)

#I will now insert the tweet movie actor data into the Tweets table using a for loop.  
insert_tweet_statement = "INSERT OR IGNORE INTO Tweets Values (?,?,?,?,?,?)"
for element in list_of_actor_tweet_instances: 
	db_cur.execute(insert_tweet_statement, element.tuple_of_tweet_data())

#I will use the database connection to commit the changes to the database. 
db_conn.commit()

#I will create a list called actor_list that holds get_tweet_info instances of each actor.
#TBD. This code is only temporary. I am looking for a way to use data that I have called from Twitter only once. I am currently making two Twitter calls, one for the Tweet class (lines 213-223) and the other to get user data. 
#actor_list = ["Auli'i Cravalho", "Helen Mirren", "Eddie Redmayne"]
#list_of_movie_info = []
#for element in actor_list: 
	#tweet_info = get_tweet_info(element)
	#list_of_movie_info.append(tweet_info)

#I will invoke the get_user_info function on each Tweet instance and store them in a list called list_of_user_info. 
#Temporary code as well. 
list_of_user_info = []
#for y in list_of_movie_info: 
	#user_info = get_user_info(y)
	#print(user_info)
	#list_of_user_info.append(user_info)
#print(list_of_user_info)
for y in list_of_instances: 
	user_info = get_user_info(y)
	#print(user_info)
	list_of_user_info.append(user_info)
#print(list_of_user_info)
#print("TRYING TO FIND THE ANSWER")
#for each_element in list_of_user_info:
	#print(type(each_element))
	#print("----------------------------------")
	#for inside_user in each_element: 
		#print(inside_user)
#print(list_of_user_info)

#In some of the JSON files that are created, I get the error below. I was wondering how this could be avoided. Is it because I'm caching too many users? 
#Traceback (most recent call last):
  #File "206_data_access.py", line 244, in <module>
    #user_info = get_user_info(y)
  #File "206_data_access.py", line 153, in get_user_info
    #user_favs = api.favorites(element["screen_name"])
  #File "/Users/sanikababtiwale/anaconda/lib/python3.5/site-packages/tweepy/binder.py", line 245, in _call
    #return method.execute()
  #File "/Users/sanikababtiwale/anaconda/lib/python3.5/site-packages/tweepy/binder.py", line 229, in execute
    #raise TweepError(error_msg, resp, api_code=api_error_code)
#tweepy.error.TweepError: Not authorized.

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

	#def return_favs_len(self):
		#return len(self.users_favs)

	def __str__(self): 
		return "{} {} {}".format(self.users_id, self.users_screen_name, self.users_favs)

	def tuple_of_users_data(self): 
		users_tuple = (self.users_id, self.users_screen_name, self.users_favs, self.users_description, self.users_location, self.users_language, self.users_followers)
		return users_tuple


print(CACHE_DICT.keys())

#movie_info = get_tweet_info("Auli'i Cravalho")
#movie_user_info = get_user_info(movie_info)
#print(len(movie_user_info))
#print(type(movie_user_info))
#print(movie_user_info)
#user_class = TwitterUser(movie_user_info)
#print(movie_user_info[3])
#for each_tweet in movie_user_info[:2]:
	#print(type(each_tweet))
	#if type(each_tweet) != type({}): 
		#print(type(each_tweet))
		#print(each_tweet)
		#print("this is the tweet")
	#print(each_tweet.keys())
	#print(type(each_tweet))
	#print(each_tweet.keys())
	#user_instance = TwitterUser(each_tweet)
	#print(str(user_instance))
list_user_instances = []
for each_element in list_of_user_info:
	#print(type(each_element))
	for inside_user in each_element: 
		user_instance = TwitterUser(inside_user)
		print(str(user_instance))
		list_user_instances.append(user_instance)
print(len(list_user_instances))


#I will give instructions to drop the Users table if it exists and create the table with the 7 column names and types of each. 
db_cur.execute("DROP TABLE IF EXISTS Users")
db_cur.execute("CREATE TABLE Users (user_id TEXT PRIMARY KEY, user_screen_name TEXT, user_favs INTEGER, user_description TEXT, user_location TEXT, user_language TEXT, user_followers INTEGER)") 

#I will insert the user info data into the Users table using a for loop. 
insert_user_statement = "INSERT OR IGNORE INTO Users Values (?,?,?,?,?,?,?)"
for element in list_user_instances:
	db_cur.execute(insert_user_statement, element.tuple_of_users_data())

db_conn.commit()

#insert_tweet_statement = "INSERT OR IGNORE INTO Tweets Values (?,?,?,?,?,?)"
#for element in list_of_actor_tweet_instances: 
	#db_cur.execute(insert_tweet_statement, element.tuple_of_tweet_data())
#I will make a query that finds the maximum number of favorited tweets for a movie title, so I will be joining the Tweets table and Movies table. I will save the result in a variable called max_num_fav_tweets.

#q3 = "SELECT COUNT(*) FROM Users, WHERE user_language = en"

#Movies ordered by number of tweets received from English speaking users. 
q3 = "SELECT Tweets.movie_id FROM Tweets INNER JOIN Users ON Tweets.user_id = Users.user_id WHERE Users.user_language = 'en'"
db_cur.execute(q3)
all_movie_actors_tweeted_eng_users = db_cur.fetchall()
movie_actors_eng_users = [x[0] for x in all_movie_actors_tweeted_eng_users]
count_movies = collections.Counter()
for id_movie in movie_actors_eng_users: 
	count_movies[id_movie] += 1
print(count_movies)
#SELECT movie_id, COUNT(user_id) FROM Tweets GROUP BY movie_id
#SELECT Tweets.movie_id, COUNT(Tweets.user_id) FROM Tweets INNER JOIN Users ON Tweets.user_id = Users.user_id WHERE Users.user_language = 'en'  GROUP BY movie_id 

#I will make a query that finds all the users who tweeted about a specific movie, so I will be joining the Tweets, Users, and Movies table. The result will be saved in a variable called users_tweets_movie.

#A set comprehension of all words with a length greater than 5 that appeared in tweets about Inside Out star Amy Poehler 
q4 = "SELECT Tweets.tweet_text FROM Tweets WHERE movie_id = 'tt2096673'"
db_cur.execute(q4)
all_tweet_text_inside_out = db_cur.fetchall()
#print(all_tweet_text_inside_out)
tweet_text_list = [text[0] for text in all_tweet_text_inside_out]
#print(tweet_text_list)

words_inside_out_tweets = []
for line in tweet_text_list: 
	the_words = line.split()
	for each_word in the_words:
		words_inside_out_tweets.append(each_word)
#print(words_inside_out_tweets)

#def words_greater_five(x):
	#if len(x) > 5: 
		#return x 

list_of_medium_words = list(filter(lambda x: len(x) > 5, words_inside_out_tweets))
#print(list_of_medium_words)
#for each_word in list_of_medium_words: 
	#print(each_word)

set_of_medium_words = {word for word in list_of_medium_words}
print(set_of_medium_words)
#dictionary_of_medium_words = {}
#for a_word in list_of_medium_words:
	#if a_word not in dictionary_of_medium_words:
		#dictionary_of_medium_words[each_word] += 1 
	#else: 
		#dictionary_of_medium_words[each_word] = 1
#most_common_word = max(word for word in list_of_medium_words)
#print(most_common_word)




#A list of users sorted by most followers to least that have favorites greater than 25. 
q5 = "SELECT user_screen_name, user_followers FROM Users WHERE user_favs > 25"
db_cur.execute(q5)
all_users_with_favs_greater_25 = db_cur.fetchall()
#print(all_users_with_favs_greater_25)
tuples_all_users = []
for each_tuple in all_users_with_favs_greater_25: 
	tuples_all_users.append(each_tuple)
#print (tuples_all_users)

sorted_users = sorted(tuples_all_users, key = lambda x: x[1], reverse = True)
print(sorted_users)

#user_with_most_followers = sorted_users[0]
#print(user_with_most_followers)



#I will process the data using four processing mechanisms. Two of the mechanics are a set comprehension called set_of_hashtags and a Counter called most_common_movie_name (which will be found from the tweets).

#I will write collected data to a "projectdata.txt" file. It will contain 3 movie titles, a twitter summary, OMDB information about each of the movies, and the date of processing. 


# Put your tests here, with any edits you now need from when you turned them in with your project plan.
#class TestProject(unittest.TestCase):
	#def test_movie_caching(self): 
		#fname = open("206_data_access_cache.json", "r")
		#filecon = fname.read()
		#fname.close 
		#self.assertTrue("Inside Out" in filecon) #testing whether movie data is in json file
	#def test_get_OMDB_data(self): 
		#movie_data = get_movie_info("Moana")
		#self.assertEqual = (movie_data, {"Title":"Inside Out","Year":"2015","Rated":"PG","Released":"19 Jun 2015","Runtime":"95 min","Genre":"Animation, Adventure, Comedy","Director":"Pete Docter, Ronnie Del Carmen","Writer":"Pete Docter (original story by), Ronnie Del Carmen (original story by), Pete Docter (screenplay), Meg LeFauve (screenplay), Josh Cooley (screenplay), Michael Arndt (additional story material by), Bill Hader (additional dialogue by), Amy Poehler (additional dialogue by), Simon Rich (additional story material by)","Actors":"Amy Poehler, Phyllis Smith, Richard Kind, Bill Hader","Plot":"After young Riley is uprooted from her Midwest life and moved to San Francisco, her emotions - Joy, Fear, Anger, Disgust and Sadness - conflict on how best to navigate a new city, house, and school.","Language":"English","Country":"USA","Awards":"Won 1 Oscar. Another 91 wins & 95 nominations.","Poster":"https://images-na.ssl-images-amazon.com/images/M/MV5BOTgxMDQwMDk0OF5BMl5BanBnXkFtZTgwNjU5OTg2NDE@._V1_SX300.jpg","Ratings":[{"Source":"Internet Movie Database","Value":"8.2/10"},{"Source":"Rotten Tomatoes","Value":"98%"},{"Source":"Metacritic","Value":"94/100"}],"Metascore":"94","imdbRating":"8.2","imdbVotes":"410,309","imdbID":"tt2096673","Type":"movie","DVD":"03 Nov 2015","BoxOffice":"$264,317,903.00","Production":"Disney/Pixar","Website":"https://www.facebook.com/PixarInsideOut","Response":"True"}) #testing whether return value of function get_OMDB_data gives correct information 
	#def test_tweet_info(self):
		#movie_tweets = get_tweet_info("moana")
		#self.assertEqual(type(movie_tweets), type([])) #testing whether return value of function get_tweet_info is a list
	#def test_tweet_info2(self):
		#movie_tweets = get_tweet_info("fantastic beasts") 
		#self.assertEqual(type(movie_tweets[0]), type({})) #testing if first element of function get_tweet_info is a dictionary
	#def test_user_info(self): 
		#movie_tweets = get_tweet_info("hundred-foot journey")
		#user_data = get_user_info(movie_tweets)
		#self.assertEqual(type(user_data), type([])) #testing if return value of function get_user_info is a dictionary
	#def test_Movie_string(self):
		#movie = get_movie_info("Moana")
		#movie_class = Movie(movie)
		#self.assertEqual(type(movie_class.__str__()), type("")) #testing if __str__() method for Movie class returns a string
	#def test_Movie_top_actor(self): 
		#movie2 = get_movie_info("Fantastic Beasts and Where to Find Them")
		#movie2_class = Movie(movie2)
		#self.assertEqual(movie2_class.top_billed_actor(), "Eddie Redmayne") #testing whether top_billed_actor method for Movie class returns correct value
	#def test_Movie_num_languages(self): 
		#movie3 = get_movie_info("The Hundred-Foot Journey")
		#movie3_class = Movie(movie3)
		#self.assertEqual(movie3_class.num_languages(), 2) #testing whether num_languages method for Movie class returns correct value
	#def test_get_movie_id(self): 
		#one_movie_id = get_movie_id("The Hundred-Foot Journey")
		#self.assertEqual(one_movie_id, "tt2980648") #testing that get_movie_id function returns correct movie id for movie 
	#def test_get_movie_id2(self): 
		#movie_id_value = get_movie_id("Moana")
		#self.assertEqual(type(movie_id_value), type("")) #testing that get_movie_id function's return value is a string 
	#def test_get_movie_actor(self): 
		#movie_actor_name = get_movie_actor("Fantastic Beasts and Where to Find Them")
		#self.assertEqual(movie_actor_name, "Eddie Redmayne") #testing that get_movie_actor function returns the correct actor name for movie 
	#def test_twtable_columns(self):
		#db_conn = sqlite3.connect("finalproject.db")
		#db_cur = db_conn.cursor()
		#db_cur.execute("SELECT * FROM Tweets")
		#tweets = db_cur.fetchall()
		#self.assertTrue(len(tweets[1]) == 6) #testing that there are 6 columns in the tweet table 
		#db_conn.close()


# Remember to invoke your tests so they will run! (Recommend using the verbosity=2 argument.)
if __name__ == "__main__":
	unittest.main(verbosity=2)	

#I will close the cursor to the database. 
db_conn.close()

