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
# urltoimg.py
# Post image from serverside, (full resolution)
#

from mumo_module import (commaSeperatedIntegers,
                         MumoModule)

from datetime import timedelta
import urllib, base64, re


class urltoimg(MumoModule):
    default_config = {'urltoimg':(
                                ('servers', commaSeperatedIntegers, []),
                                ('keyword', str, '!kuva')
                                )
                    }
    
    def __init__(self, name, manager, configuration = None):
        MumoModule.__init__(self, name, manager, configuration)
        self.murmur = manager.getMurmurModule()
        self.keyword = self.cfg().urltoimg.keyword

    def connected(self):
        manager = self.manager()
        log = self.log()
        log.debug("Register for Server callbacks")
        
        servers = self.cfg().urltoimg.servers
        if not servers:
            servers = manager.SERVERS_ALL
            
        manager.subscribeServerCallbacks(self, servers)
    
    def disconnected(self): pass
    
    def sendMessage(self, server, user, message, msg):
        server.sendMessageChannel(user.channel, False, msg)
    #
    #--- Server callback functions
    #
    
    def userTextMessage(self, server, user, message, current=None):
        if message.text.startswith(self.keyword):            
            msg = message.text[len(self.keyword):].strip()
            link = re.findall(r'href=[\'"]?([^\'" >]+)', msg)
            img = urllib.urlopen(link[0])
            size = int(img.info().getheaders("Content-Length")[0])/1024
            if size < 256:
                encoded = base64.b64encode(img.read())
                msg = '<img src="data:image/jpeg;charset=utf-8;base64,' + str(encoded) + '"/>'
                self.sendMessage(server, user, message, msg)
            else:
                #TODO: add something from standard libraries to drop quality down.
                msg = "image too large to post."
                self.sendMessage(server, user, message, msg)
            return


            
    
    def userConnected(self, server, state, context = None): pass
    def userDisconnected(self, server, state, context = None): pass
    def userStateChanged(self, server, state, context = None): pass
    
    def channelCreated(self, server, state, context = None): pass
    def channelRemoved(self, server, state, context = None): pass
    def channelStateChanged(self, server, state, context = None): pass
