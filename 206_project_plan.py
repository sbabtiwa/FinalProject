## Your name: Sanika Babtiwale 
## The option you've chosen: Option 2 

# Put import statements you expect to need here!
import unittest
import collections 
import tweepy 
import twitter_info 
import json 
import sqlite3 
import itertools 

# Write your test cases here.
class TestProject(unittest.TestCase):
	def test_movie_caching(self): 
		fname = open("206_final_project_cache.json", "r")
		filecon = fname.read()
		fname.close 
		self.assertTrue("Moana" in filecon) #testing whether movie data is in json file
	def test_get_OMDB_data(self): 
		movie_info = get_OMDB_data("Moana")
		self.assertEqual = (movie_info, {"Title":"Moana","Year":"2016","Rated":"PG","Released":"23 Nov 2016","Runtime":"107 min","Genre":"Animation, Adventure, Comedy","Director":"Ron Clements, Don Hall, John Musker, Chris Williams","Writer":"Jared Bush (screenplay), Ron Clements (story by), John Musker (story by), Chris Williams (story by), Don Hall (story by), Pamela Ribon (story by), Aaron Kandell (story by), Jordan Kandell (story by)","Actors":"Auli'i Cravalho, Dwayne Johnson, Rachel House, Temuera Morrison","Plot":"In Ancient Polynesia, when a terrible curse incurred by the Demigod Maui reaches an impetuous Chieftain's daughter's island, she answers the Ocean's call to seek out the Demigod to set things right.","Language":"English","Country":"USA","Awards":"Nominated for 2 Oscars. Another 11 wins & 66 nominations.","Poster":"https://images-na.ssl-images-amazon.com/images/M/MV5BMjI4MzU5NTExNF5BMl5BanBnXkFtZTgwNzY1MTEwMDI@._V1_SX300.jpg","Ratings":[{"Source":"Internet Movie Database","Value":"7.7/10"},{"Source":"Rotten Tomatoes","Value":"95%"},{"Source":"Metacritic","Value":"81/100"}],"Metascore":"81","imdbRating":"7.7","imdbVotes":"93,475","imdbID":"tt3521164","Type":"movie","DVD":"07 Mar 2017","BoxOffice":"$248,558,024.00","Production":"Walt Disney Pictures","Website":"http://movies.disney.com/moana","Response":"True"}) #testing whether return value of function get_OMDB_data gives correct information 
	def test_tweet_info(self):
		movie_tweets = get_tweet_info("moana")
		self.assertEqual(type(movie_tweets), type([])) #testing whether return value of function get_tweet_info is a list
	def test_tweet_info2(self):
		movie_tweets = get_tweet_info("fantastic beasts") 
		self.assertEqual(type(movie_tweets[10]), type({})) #testing if 11th element of function get_tweet_info is a dictionary
	def test_Movie_string(self):
		movie = Movie("Moana")
		self.assertEqual(type(movie.__str__()), type("")) #testing if __str__() method for Movie class returns a string
	def test_Movie_top_actor(self): 
		movie = Movie("Fantastic Beasts and Where to Find Them")
		self.assertEqual(top_billed_actor, "Eddie Redmayne") #testing whether top_billed_actor method for Movie class returns correct value
	def test_Movie_num_languages(self): 
		movie = Movie("The Hundred-Foot Journey")
		self.assertEqual(movie.num_languages, 2) #testing whether num_languages method for Movie class returns correct value 
	def test_twtable_columns(self):
		db_conn = sqlite3.connect("finalproject_movie.db")
		db_cur = db_conn.cursor()
		db_cur.execute("SELECT * FROM Tweets")
		tweets = db_cur.fetchall()
		self.assertEqual(len(tweets[1]) == 6) #testing that there are 6 columns in the tweet table 
		db_conn.close()
	def test_set_of_hashtags(self): 
		self.assertEqual(type(movie_hashtags), type({})) 
		#testing that data processing tool containing all of the hashtags used for the three movies is a set

if __name__ == "__main__":
	unittest.main(verbosity=2)	

## Remember to invoke all your tests...


