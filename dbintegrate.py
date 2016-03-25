#!/usr/bin/env python
# -*- coding: utf-8

# Copyright (C) 2013 Ilari Lind <>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:

# - Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# - Neither the name of the Mumble Developers nor the names of its
#   contributors may be used to endorse or promote products derived from this
#   software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# `AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE FOUNDATION OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#
# dbintegrate.py
# Integration with postgresql database
#

from mumo_module import (commaSeperatedIntegers,
                         MumoModule)

from datetime import timedelta
import urllib, base64, re, psycopg2

# Need to create dbdetails.py file
from dbdetails import dbname, dbuser, dbpass


class dbintegrate(MumoModule):
    default_config = {'dbintegrate':(
                                ('servers', commaSeperatedIntegers, []),
                                ('keyword', str, '!kuva')
                                )
                    }
    
    def __init__(self, name, manager, configuration = None):
        MumoModule.__init__(self, name, manager, configuration)
        self.murmur = manager.getMurmurModule()
        self.keyword = self.cfg().dbintegrate.keyword
        try:
            self.conn= psycopg2.connect("dbname="+dbname+" user="+dbuser+" host='localhost' password="+dbpass)
            self.cur = self.conn.cursor()
        except:
            print "Couldn't connect to the db."

    def connected(self):
        manager = self.manager()
        log = self.log()
        log.debug("Register for Server callbacks")
        
        servers = self.cfg().dbintegrate.servers
        if not servers:
            servers = manager.SERVERS_ALL
            
        manager.subscribeServerCallbacks(self, servers)
    
    def disconnected(self): pass
    
    def sendMessage(self, server, user, message, msg):
        server.sendMessageChannel(user.channel, False, msg)
    #
    #--- Server callback functions
    #
    
    def userTextMessage(self, server, user, message, current=None): pass

    def userConnected(self, server, state, context = None):
        self.updateUsers(server)
    def userDisconnected(self, server, state, context = None):
        self.updateUsers(server)
    def userStateChanged(self, server, state, context = None):
        self.updateUsers(server)

    def channelCreated(self, server, state, context = None): pass
    def channelRemoved(self, server, state, context = None): pass
    def channelStateChanged(self, server, state, context = None): pass

    def updateUsers(self, server):
        # Get users
        users = server.getUsers()
        channels = server.getChannels()

        # Step through each user
        for user in users.values():
            insert_user = "INSERT INTO mumblewebapp_user (userid, username) VALUES ("+str(user.userid)+", '"+user.name+"') ON CONFLICT (userid) DO NOTHING;"
            #print "id=",user.userid, 
            #print "name=",user.name, 
            #print "channel=",user.channel, channels[user.channel].name
            try:
                self.cur.execute(insert_user)
                self.conn.commit();
                #print self.cur
                #print "successfully inserted row!"
            except psycopg2.Error as exp:
                #print "Couldn't insert record", user.userid, user.name, user.channel, channels[user.channel].name
                print exp
            #print insert_user
            #print 
        
