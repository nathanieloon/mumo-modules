#!/usr/bin/env python
# -*- coding: utf-8

#
# bot.py
# The mumble server bot
# Author: Nate Oon
# Updated: 2015-5-15

from mumo_module import (commaSeperatedIntegers,
                         MumoModule)

from datetime import timedelta, time

from HTMLParser import HTMLParser
import re, json, urllib, time, random, isodate, requests
from key import api_key
from BeautifulSoup import BeautifulSoup

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


class YoutubeException(Exception):
    def __init__(self, payload, msg=None):
        if not msg:
            self.msg = "An error occurred with the YouTube API. It's probably an issue with your key. RETURN: {0}".format(payload)
        Exception.__init__(self, self.msg)


class bot(MumoModule):
    default_config = {'bot':(
                                ('servers', commaSeperatedIntegers, []),
                                ('roulette', str, '!rr'),
                                ('roll', str, '!roll'),
                                ('rollAll', str, '!allRoll'),
                                ('compendium', str, '!dota'),
                                ('joke', str, '!joke'),
                                ('register', str, '!register'),
                                ('unregister', str, '!unregister')
                                )
                    }
    
    def __init__(self, name, manager, configuration = None):
        MumoModule.__init__(self, name, manager, configuration)
        self.murmur = manager.getMurmurModule()
        #self.keyword = self.cfg().bot.keyword
        self.roll = self.cfg().bot.roll
        self.rollAll = self.cfg().bot.rollAll
        self.roulette = self.cfg().bot.roulette
        self.compendium = self.cfg().bot.compendium
        self.joke = self.cfg().bot.joke
        self.register = self.cfg().bot.register
        self.unregister = self.cfg().bot.unregister

    def connected(self):
        manager = self.manager()
        log = self.log()
        log.debug("Register for Server callbacks")
        
        servers = self.cfg().bot.servers
        if not servers:
            servers = manager.SERVERS_ALL
            
        manager.subscribeServerCallbacks(self, servers)
    
    def disconnected(self): pass
    
    def sendMessage(self, server, user, message, msg):
        if message.channels:
            server.sendMessageChannel(message.channels[0], False, msg)
        else:
            server.sendMessage(user.session, msg)
            server.sendMessage(message.sessions[0], msg)
    #
    #--- Server callback functions
    #
    
    def userTextMessage(self, server, user, message, current=None):
        msg = message.text
        print "BOT MSG:", message
        #self.sendMessage(server, user, message, msg)

        if message.text.startswith("!test"):
            self.sendMessage(server, user, message, "we found it, yah!")

        # Imgur info
        imgur_info = self.imgurDetect(message)

        # GFYcat info
        gfy_info = self.gfyDetect(message)

        # Youtube info
        youtube_info = self.youtubeDetect(message)

        # Dice rolling
        if message.text.startswith(self.rollAll):
            dice_info = self.diceRoller(server, user, message)
            self.sendMessage(server, user, message, dice_info)

        # Individual roll
        if message.text.startswith(self.roll):
            roll_info = self.diceRoll(server, user, message)
            self.sendMessage(server, user, message, roll_info)

        # Russian Roulette
        if message.text.startswith(self.roulette):
            print "FOUND ITTTTTTTTTTTTTT"
            roulette_info = self.russianRoulette(server, user, message)
            self.sendMessage(server, user, message, roulette_info)
	
        # Compendium Amount
        if message.text.startswith(self.compendium):
            compendium_info = self.compendiumInfo(message)
            self.sendMessage(server, user, message, compendium_info)
        
        # Jokes
        if message.text.startswith(self.joke):
            joke = self.jokes(message)
            self.sendMessage(server, user, message, joke)

        # Register for tourney
        if message.text.startswith(self.register):
            reg = self.registerUser(user, message)
            self.sendMessage(server, user, message, reg)

        # Unregister for tourney
        if message.text.startswith(self.unregister):
            unreg = self.unregisterUser(user, message)
            self.sendMessage(server, user, message, unreg)

        print "RETURNED INFO", youtube_info
        if len(youtube_info) > 0:
            self.sendMessage(server, user, message, youtube_info)
        
        print "IMGUR INFO:", imgur_info
        if len(imgur_info) > 0:
            self.sendMessage(server, user, message, imgur_info)
        
        print "GFY INFO:", gfy_info
        if len(gfy_info) > 0:
            self.sendMessage(server, user, message, gfy_info)
    
    def userConnected(self, server, state, context = None): pass
    def userDisconnected(self, server, state, context = None): pass
    def userStateChanged(self, server, state, context = None): pass
        
    
    def channelCreated(self, server, state, context = None): pass
    def channelRemoved(self, server, state, context = None): pass
    def channelStateChanged(self, server, state, context = None): pass


    # RUSSIAN ROULETTE METHOD
    def russianRoulette(self, server, user, message):
        # Make noise
        firing = random.randrange(2, 6)
        for x in range(firing, -1, -1):
            time.sleep(1)
            if x != 0:
                self.sendMessage(server, user, message, "*click*, the chamber was empty...")

        # Get users
        users = server.getUsers()
        # Get random victim
        session_list = {}
        
        # Get users in the channelz
        count = 0
        for u in users.values():
            if u.channel == message.channels[0]:
                session_list[u.session] = u.name
                count += 1
                
        # Get a random victim
        rand = random.randrange(0, len(session_list.keys()))

        # Get the victim's name
        usr_count = 0
        user_name = session_list[session_list.keys()[rand]]
        #for u in session_list.keys():
        #    print u, session_list[u]
        #    if u == rand:
        #        user_name = session_list[u]
        #    usr_count += 1

        print "Kicking", user_name
        #print "session_list", session_list

        server.kickUser(session_list.keys()[rand], "You got shot!")
        return 'The gun is loaded... {0} was shot!<br><img src="http://i.imgur.com/cIBCVa6.jpg" width="250" />'.format(user_name)


    # INDIVIDUAL ROLLING METHOD
    def diceRoll(self, server, user, message):
        # Roll the die
        rand = random.randrange(0, 100)
        output = "<b>{0}</b> rolled {1}".format(user.name, rand)
        return output

    # CHANNEL BASED ROLLING
    def diceRoller(self, server, user, message):
        # Get users
        users = server.getUsers()
        rolls = {}
        # Step through users
        for usr in users.values():
            #print usr
            print "USR CHANNEL:", usr.channel, user.channel
            if usr.channel == user.channel:
                print "YAH"
                rand = random.randrange(0, 100)
                rolls[usr.name] = rand
        output = "<h2> Dice Roller </h2>"
        print rolls
        for roll in rolls.items():
            output += "<b>{0}</b> rolled {1} <br/>".format(roll[0], roll[1])
    
        print "DICE OUTPUT:", output
        return output
    
    # IMGUR THUMBNAIL DISPLAYING
    def imgurDetect(self, message):
        # Strip the HTML from the message
        msg = message.text
        link = strip_tags(msg)
        #print "TEST", link
        # If the message has an imgur link
        if "i.imgur.com" in msg:
            split_link = link.split(".")
            split_len = len(split_link) - 2 
            split_link[split_len] += "m"
            join_link = ".".join(split_link)
            print join_link
            img = '<br/><a href="{0}"><img src="{1}" width="250"/></a>'.format(link, join_link)
            print "TEST", link, join_link
            return img
        else:
            return ""

    # GYFCAT THUMBNAIL DISPLAYING
    def gfyDetect(self, message):
        # Strip HTML
        msg = message.text
        link = strip_tags(msg)
        # If there's a gfycat link
        if "gfycat.com" in msg:
            gfy = link.split(".com")[1].split("/")[1]
            print "GFY = ", gfy
            thumbnail_link = "http://thumbs.gfycat.com/" + gfy + "-thumb100.jpg"
            img = '<br/><a href="{0}"><img src="{1}" width="200"/></a>'.format(link, thumbnail_link)
            return img
        else:
            return ""

    # YOUTUBE PREVIEW DISPLAYING
    def youtubeDetect(self, message):
        msg = message.text
        link = strip_tags(msg)
        youtube_regex = (
            r'(https?://)?(www\.)?'
            '(youtube|youtu|youtube-nocookie)\.(com|be)/'
            '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
        youtube_regex_match = re.match(youtube_regex, link)
        if youtube_regex_match:
            video_id = youtube_regex_match.group(6)
            youtube_info = "https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails&id="+video_id+"&key="+api_key
            #print "API URL:", youtube_info
            try:
                youtube_json = json.load(urllib.urlopen(youtube_info))
                #print "JSON:", youtube_json
                #print "test", youtube_json['items'][0]['snippet']['title']
                if 'items' not in youtube_json:
                    raise YoutubeException(youtube_json)
                video_duration = youtube_json['items'][0]['contentDetails']['duration']
                video_time = isodate.parse_duration(video_duration)
                video_title = youtube_json['items'][0]['snippet']['title']
                video_thumb = youtube_json['items'][0]['snippet']['thumbnails']['high']['url']
            except YoutubeException:
                raise
                
            youtube_template = '<br/><a href="https://youtu.be/{0}">{1} ({2})</a>\
                                <a href="https://youtu.be/{3}"><img src="{4}" \
                                width="250"/></a>'\
                                .format(video_id,
                                        video_title, 
                                        video_time,
                                        video_id,
                                        video_thumb)
            print "YOUTUBE INFO:", youtube_template
            return youtube_template
    
        return ""

    # Display the current prizepool for the 2015 International
    def compendiumInfo(self, message):
        # Scrape HTML
	    soup = BeautifulSoup(urllib2.urlopen("http://www.dota2.com/international/compendium"))
	    html = soup.find(id="PrizePoolText")
        # Get value
	    value = strip_tags(str(html))
	    #print value
	    return "The 2015 International prizepool is currently <b>" + value + "</b>"

    # Jokes function
    def jokes(self, message):
        # Jokes
        jokes = ["My friend gave me his Epi-Pen as he was dying. <br>"+
                   "It seemed very important to him that I have it.",
                 "You can never lose a homing pigeon - if your homing pigeon doesn't come back, "+ 
                   "what you've lost is a pigeon.",
                 "A family walks into a hotel and the father goes to the front desk and says 'I hope the porn is disabled' <br>"+
                   "The guy at the desk replies. 'It's just regular porn you sick fuck.'",
                 "A man walks into a library and says to the librarian, 'Do you have that book for men with small penises?'<br>"+
                   "The librarian looks on her computer and says, 'I don't know if it's in yet.'<br>"+
                   "'Yeah that's the one'",
                 "Two deer walk out of a gay bar. One turns and says to the other, "+
                   "I can't believe I just blew thirty bucks in there.",
                 "How many potatoes does it take to kill an Irishman? Zero.",
                 "What's the difference between a well dressed man on a bike and a poorly dressed man on a unicycle?<br>"+
                   "Attire.",
                 "Sixteen sodium atoms walk into a bar…followed by Batman.",
                 "What did the kid with no hands get for Christmas?<br>"+
                   "Gloves.<br>"+
                   "Just kidding, he hasn't gotten the box open yet.",
                 "What would a rapper who laughs a lot call himself? Lolol Cool J",
                 "Which came first, the chicken or the egg?<br>"+
                   "Neither, the rooster did.",
                 "Never trust an ironworker with your belongings. He's bound to steel them.",
                 "What did one ocean say to the other ocean? Nothing, he just waved."
                ]
        # Get a joke
        rand = random.randrange(0, len(jokes))
        joke = jokes[rand]
        # Return the joke
        return joke

    # Register user to tourney
    def registerUser(self, user, message):
        payload = {"f_uname": user.name}
        r = requests.post("https://52.64.11.229:8000/amazon_site/default/api/registeruser", data=payload, verify=False)
        print r.status_code
        if r.status_code == 409:
            return "You are already registered for the tournament."
        elif r.status_code == 200:
            return "You have successfully registered for the tournament."
        else:
            return "Something went wrong. (ERROR CODE: " + r.status_code + ")"

    # Unregister user from tourney
    def unregisterUser(self, user, message):
        payload = {"f_uname": user.name}
        r = requests.delete("https://52.64.11.229:8000/amazon_site/default/api/unregisteruser", data=payload, verify=False)
        print r.status_code
        if r.status_code == 200:
            return "You have been successfully removed from the tournament."
        else:
            return "There was an error removing you from the tournament."
