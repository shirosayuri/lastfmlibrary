# lastfmlibrary

Well, ok, someday I'll write here cool unofficial api lib for last.fm, but not today.
Today it's only small not perfect data visualisation with sqlite, Tableau Public and mine 10-years library of tracks on Last.fm.
Thanks a lot to [Dataquest's Tutorial](https://www.dataquest.io/blog/last-fm-api-python/) and to [SQLite](https://www.sqlitetutorial.net/) tutorials and so on.
While I tried to write it I've studied a lot. 

### Sqlite Functions
Here I tried to create one functional class for work with SQLite as I thought it'll be ok to use this db with Tableau Public (spoiler: it's not).
First, you init your db-file. When you init class, the db-file creates automatically. 
Then, **execute** func is for all execute processes to use in all other's funcs.
**drop_table** is for deleting table with no any further questions.
**create_table** is for creating table, where you need to initialize table schema in dict.
**insert_row** is for inserting one row. Here you may decide if you want to replace the row by primary key or not.
**insert_table** is for inserting whole table. Well, it's just a cycle, yep. 
**update_raw** is for updating a row in the table. If you don't give them any condition you may update whole **fkn** table. Be careful.
**delete_raw** is for deleting a row, be careful here too. 
**select_date** is for taking any data from your table, with condition, or not, who cares. It'll give you a list of dicts. 

### Last.Fm Functions
I love [last.fm](http://www.lastfm.ru/) very much and use it since 2009. I got really ___huge___, I think, [scrobbled library](https://www.last.fm/ru/user/ShiroSayuri). So I just hope they will not ban me for this awkward code. Jeez.
First, you need to init your application. At Dataquest's Tutorial, I meant early, it really cool discribed: how to get api_key and wtf user_agent is. Shortly: user_agent is needed to last.fm so they'll be able to understand who the hell ddos'ing their api.
**lastfm_get** is func for getting any api page by method. Here I use request cache and if result not in cache - wait for 0.25sec, so not ddos'ing api.
**get_token** is for obtain token, but I never used it yet.
**get_library_page** is for obtain one page of library of some user. It's where your loved artist writen. 
**get_recent_track** is for obtain one page of ever scrobbled tracks. 
**get_library** is for obtain whole library or whole scrobbled tracks.
**get_track_info** is for obtain info about one track: I wanted to know top tags and duration of song so I'll be able to know, what I was able to do for whole that time.

### Functions
It's a small pack of unnecessary funcs, like taking secrets from json file, or printing beautiful json, whatever. 

### Main
Is just example, ofc whole work was in file test.py while I was not really sure ___it's alive___.

### Where the hell is visualisation?
Well, as I said, Tableau Public do not want to work with SQLite database. So, I used some pandas magic, that you may find at main file, to create data sets to work with.
I have no discover what story I wanted to create, I just wanted to share the library. But anyway at overview you may notice some points where scrobbling was near zero and were it grow. I may find where I've started yandex.music for example.
But anyway, I've studied much. See on [Tableau Public](https://public.tableau.com/profile/shirosayuri#!/vizhome/ShiroSayuriLastFmVisualisation/ShiroSayurisLibrary).
