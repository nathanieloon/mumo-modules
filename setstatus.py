#!/usr/bin/env python
# -*- coding: utf-8
#
# Copyright (C) 2011 Stefan Hacker <dd0t@users.sourceforge.net>
# Copyright (C) 2012 Natenom <natenom@googlemail.com>
# All rights reserved.
#
# setstatus is based on the script seen.py
# (made by dd0t) from the Mumble Moderator project, available at
# http://gitorious.org/mumble-scripts/mumo
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
# setstatus.py
# Allows registered users to set a comment in square brackets behind their names.
#

from mumo_module import (commaSeperatedIntegers,
			 commaSeperatedBool,
                         MumoModule)
import pickle
import re

class setstatus(MumoModule):
    default_config = {'setstatus':(
                                ('servers', commaSeperatedIntegers, []),
                                ),
                                lambda x: re.match('(all)|(server_\d+)', x):(                                
                                ('setstatus', str, '!ss'),
                                ('delstatus', str, '!ds'),
				('length', int, 20)
                                )
                    }
    
    def __init__(self, name, manager, configuration = None):
        MumoModule.__init__(self, name, manager, configuration)
        self.murmur = manager.getMurmurModule()

    def connected(self):
        manager = self.manager()
        log = self.log()
        log.debug("Register for Server callbacks")
    
        servers = self.cfg().setstatus.servers
        if not servers:
            servers = manager.SERVERS_ALL
    
        manager.subscribeServerCallbacks(self, servers)

    def disconnected(self): pass
    
    def getuserorigname(self, username):
        p=re.compile('^[^\[]+') #findet alles bis zur ersten [ Klammer  
        return p.findall(username)[0].strip() #Leerzeichen am Anfang/Ende entfernen

    #--- Server callback functions
    # 

    def userTextMessage(self, server, user, message, current=None):
        try:
            scfg = getattr(self.cfg(), 'server_%d' % server.id())
        except AttributeError:
            scfg = self.cfg().all
      
        #Only allow registered Users to set a status
        if user.userid > 0:
            if message.text.startswith(scfg.setstatus):
                statuscode=message.text[len(scfg.setstatus):].strip()   
		userstate=server.getState(int(user.session))
		userstate.name="%s [%s]"  % (self.getuserorigname(userstate.name), statuscode[:scfg.length])
		server.setState(userstate)

            if message.text.startswith(scfg.delstatus):
		userstate=server.getState(int(user.session))
		userstate.name=self.getuserorigname(userstate.name)
		server.setState(userstate)

    def userConnected(self, server, state, context = None): pass
    def userDisconnected(self, server, state, context = None): pass
    def userStateChanged(self, server, state, context = None): pass
    def channelCreated(self, server, state, context = None): pass
    def channelRemoved(self, server, state, context = None): pass
    def channelStateChanged(self, server, state, context = None): pass     
