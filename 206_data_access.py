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

#moana = omdb.get(title = "Moana", year = 2016, fullplot = "short", tomatoes = True)
#print(moana)
CACHE_FILE = "206_data_access_cache.json"
try: 
	cached_data = open(CACHE_FILE, "r")
	file_contents = cached_data.read()
	cached_data.close()
	CACHE_DICT = json.loads(file_contents)
except: 
	CACHE_DICT = {}

# I will define a function called get_tweet_info that caches search term data from Twitter. Then, I will invoke the function and store the return value in a variable called movie_tweets. 
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
	return CACHE_DICT

movie_tweets = get_tweet_info("Moana")
#print(movie_tweets)

print("--------------------------------------------------------")

#I will define a function called get_movie_info that caches movie data from OMDB. Then, I will invoke the function and store the return value in a variable called movie_info. 
def get_movie_info(s, y):
	unique_key = "omdb_{}".format(s)
	if unique_key in CACHE_DICT: 
		print("Using cached data for", s)
		pass 
	else: 
		print("Getting new data from omdb for", s)
		movie_data = omdb.get(title = s, year = y, fullplot = False, tomatoes = True)
		CACHE_DICT[unique_key] = movie_data
		fileref = open(CACHE_FILE, "w")
		fileref.write(json.dumps(CACHE_DICT))
		fileref.close()
	return CACHE_DICT

movie_info = get_movie_info(s = "Moana", y= 2016)
movie_info2 = get_movie_info(s = "The Hundred-Foot Journey", y = 2014)
movie_info3 = get_movie_info(s = "Fantastic Beasts and Where to Find Them", y = 2016)
#print(movie_info["omdb_Moana"])

#I will define a class called Movie that takes the dictionary with the movie's information as input to its constructor. 
class Movie(object):
	def __init__(self, movie_dict):
		self.movie_title = movie_dict["title"]
		self.movie_rating = movie_dict["imdb_rating"]
		self.movie_languages = movie_dict["language"]
		self.cast_list = movie_dict["actors"]

	def num_languages(self):
		return len(self.movie_languages.split())

	def top_billed_actor(self): 
		return self.cast_list.split(",") [0]

	def __str__(self):
		return "The movie '{}' has been rated {} stars out of 10 on IMDB and can be found in {} language(s). One of the main actors in the movie is {}.".format(self.movie_title, self.movie_rating, self.num_languages(), self.top_billed_actor())
		



moana = Movie(movie_info["omdb_Moana"])
print(moana.movie_title)
print(moana.movie_rating)
print(moana.movie_languages)
print(moana.top_billed_actor())
print(moana.__str__())
print("------------------------------------")
hundred_foot = Movie(movie_info2["omdb_The Hundred-Foot Journey"])
print(hundred_foot.movie_rating)
print(hundred_foot.num_languages())
#print(hundred_foot.cast_list)
print(hundred_foot.top_billed_actor())
print(hundred_foot.__str__())
print("------------------------------------")
fantastic_beasts = Movie(movie_info3["omdb_Fantastic Beasts and Where to Find Them"])
print(fantastic_beasts.movie_rating)
print(fantastic_beasts.top_billed_actor())









# Put your tests here, with any edits you now need from when you turned them in with your project plan.

# Remember to invoke your tests so they will run! (Recommend using the verbosity=2 argument.)
#if __name__ == "__main__":
#	unittest.main(verbosity=2)	

