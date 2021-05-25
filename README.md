# everyday_weather_tlgrm
Simple sturdy-pet project. The aim of this project is to get familiar with Yandex Weather and Telegram Bot APIs and generate personal habbit of finding out weather before going to work / back home. 
*** 
Problem that this project solved: I always have problem when going out - not to check the weather. Thus, I can find myself dressed warm during hot weather or vice versa, without an umbrealla during a rainy day and so on. This bot helps me a lot. Moreover, it may be viewed as an interesting realistaion of widget buy in messenger itself.

*** 

General information:
* Bot sends current weather and foreccast for midday as well as evening at around 8 a.m. during workdays (10 a.m. at weekdays)
* Bot sends only current weather at around 7 p.m.

*** 

Future plans of the project:
* Move to own server (so that I could refactor code to be more beautiful - now beauti is lost due to fact that free accounts limitations should be worked around)
* Make bot accessible for any telegram user with possibility to change settings to own preference (connecting database via SQL Alchemy):
-- set location
-- set time of sending messages
-- custom messages

*** 

Limitations:
* Works only for one user - me
* Works only with preset location - Moscow, Russia
* Heroku free account works only if deployed code make request at least once a hallf an hour (once in 20 min bot requests yandex.ru)
* Yandex Weather free API plan includes only 50 requests per day

*** 

Change log:

v. 0.0.3 - code refactoring: swithced yandex weather test access to api (trial finished). Now the limit is 50 requests a day. + heroku free account limit updated - to make at least one request in 30 minutes. 

v. 0.0.2 - small code refactoring and added evening message

v. 0.0.1 - first ever version: works only for one user, for preset location - Moscow, Russia
