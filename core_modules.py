# -*- coding: UTF-8 -*-
#core modules for bhottu
#Filename: core_modules.py

from config import *
from utils import *
import os
import string
import time

def SetUser(parsed):
    if parsed['event'] == '439':
        log('SetUser(): Sending USER'+IDENT+' '+MODE+' '+REALNAME)
        return('USER %s %s * :%s\r\n' % (IDENT,MODE,REALNAME))

def SetNick(parsed):
    if parsed['event'] == '439':
        log('SetNick(): Sending NICK '+NICK)
        return('NICK %s \r\n' % NICK)

def SetVhost(parsed):
    if VHOST == True:
        if parsed['event'] == '376':
            log('SetVhost(): Registering nick')
            return('PRIVMSG nickserv :identify '+NICK_PASS+' \r\n')

def SetChannel(parsed):
    if VHOST == True:
        if parsed['event'] == 'notice':
            if 'Password accepted - you are now recognized.' in parsed['event_msg']:
                log('SetChannel(): Joining '+CHANNEL)
                return('JOIN %s \r\n' % CHANNEL)
    elif parsed['event'] == '376':
        log('SetChannel(): Joining '+CHANNEL)
        return('JOIN %s \r\n' % CHANNEL)

def Pong(parsed):
    if parsed['event'] == 'PING':
        log('Pong(): PONG')
        return'PONG :' + parsed['event_msg'] + '\r\n'

