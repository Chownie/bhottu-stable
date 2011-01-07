# -*- coding: UTF-8 -*-
#Addon modules for bhottu
#Filename: addon_modules.py

from config import *
from utils import *
import os
import re
import string
import time
import urllib2
import sqlite3


#### VARIABLES ####

that_was = None

#### DATABASE INITS ####

def dbInit():
    #Projects
    conn = sqlite3.connect('dbs/projects.db',isolation_level=None)
    db = conn.cursor()
    db.execute('''create table if not exists projects (name text, version text, description text, maintainers text, language text, status text)''')
    conn.commit()
    db.close()
    ##Points
    conn = sqlite3.connect('dbs/points.db',isolation_level=None)
    db = conn.cursor()
    db.execute('''create table if not exists nickplus (name text, points int)''')
    conn.commit()
    conn.close()
    ##Quotes
    conn = sqlite3.connect('dbs/quotes.db',isolation_level=None)
    db = conn.cursor()
    db.execute('''create table if not exists quote (name text, quotation text)''')
    conn.commit()
    conn.close()
    ##reply
    conn = sqlite3.connect('dbs/reply.db',isolation_level=None)
    db = conn.cursor()
    db.execute('''create table if not exists replies (trigger text, reply text)''')
    conn.commit()
    conn.close()
    ##lines
    conn = sqlite3.connect('dbs/lines.db',isolation_level=None)
    db = conn.cursor()
    db.execute('''create table if not exists lines (name text, message text)''')
    conn.commit()
    conn.close()
    #Greetings
    conn = sqlite3.connect('dbs/greetings.db',isolation_level=None)
    db = conn.cursor()
    db.execute('''create table if not exists greetings (nick text, greeting text)''')
    conn.commit()
    conn.close()

#### ADDONS ####

def nickPlus(parsed):
    if parsed['event'] == 'privmsg':
        message = parsed['event_msg']
        nick = parsed['event_nick']
        uname = re.search('^\w+(?=\+{2})', message)
        pointnum = None
        if uname is not None:
            log(uname.group())
            uname = uname.group()
            log("message: " + message)
            log("nick: " + nick)
            log("uname: " + uname)
            uname = uname.replace('++','').rstrip()
            if uname == nick:
                return_msg = sendPM(nick, "Plussing yourself is a little sad, is it not?")
                return
            uname = uname.replace('++','')
            conn = sqlite3.connect('dbs/points.db',isolation_level=None)
            db = conn.cursor()
            try:
                pointnum = int(db.execute("SELECT points FROM nickplus WHERE name=?",[uname]).fetchall()[0][0])
            except:
                log("Something went wrong!")
            if pointnum is not None:
                return_msg = sendMsg(None, 'incremented by one')
                pointnum += 1
                db.execute("UPDATE nickplus SET points=? WHERE name=?",[pointnum,uname])#
                log("Incremented by 1")
            elif pointnum == None:
                return_msg = sendMsg(None, 'Added record')
                db.execute("INSERT INTO nickplus (name, points) VALUES (?, ?)",[uname,1])
                log("Incremented by 1")
            conn.close()
            return return_msg

def queryNick(parsed):
    if parsed['event'] == 'privmsg':
        message = parsed['event_msg']
        nick = parsed['event_nick']
        combostring = NICK + ", tell me about "
        conn = sqlite3.connect('dbs/points.db',isolation_level=None)
        if combostring in message:
            uname = message.split(combostring)[1].replace('++','')
            log(uname)
            db = conn.cursor()
            try:
                pointnum = int(db.execute("SELECT points FROM nickplus WHERE name=?",[uname]).fetchall()[0][0])
                return_msg = sendMsg(nick, 'Points for '+uname+' = ' + str(pointnum))
            except:
                pass
            conn.close()
            return return_msg

def outputTitle(parsed):
    if parsed['event'] == 'privmsg':
        message = parsed['event_msg']
        umessage = None
        if message.rfind("http://") != -1:
            umessage = re.search('htt(p|ps)://.*', message)
        if umessage is not None:
            try:
                log(umessage.group())
                #req = urllib2.Request(umessage.group(0))
                response = urllib2.urlopen(umessage.group(0))
                html = response.read()
                response.close()
                tt=html.split('<title>')[1]
                html=tt.split('</title>')[0].replace('\r','')
                html = html.replace('\n','').lstrip()
                return_msg = sendMsg(None, "Site title: %s" % (html))
            except:
                return_msg = sendMsg(None, 'Cannot find site title')
            return return_msg

def projectWiz(parsed):

    def projectWizList(what): #NOT-INCLUDE
        what = what.split(None, 1)
        if 'open' in what[0]:
            query = "SELECT * FROM projects WHERE status='OPEN'"
        elif what[0] == 'closed':
            query = "SELECT * FROM projects WHERE status='CLOSED'"
        elif what[0] == 'all':
            query = "SELECT * FROM projects"
        elif what[0] == 'lang':
            if len(what) < 2:
                return sendMsg(None, 'Syntax: lang [lang]')
            query = "SELECT * FROM projects WHERE language="'\''+what[1]+'\''
        else:
            return sendMsg(None, 'Syntax: list [ open, closed, all, lang [lang] ]')
        conn = sqlite3.connect('dbs/projects.db',isolation_level=None)
        db = conn.cursor()
        db.execute(query)
        derp = db.fetchall()
        return_list = []
        for row in derp:
            return_list.append(sendMsg(None, "%s | %s | %s | %s | %s | %s" % (row[0],row[1],row[2],row[3],row[4],row[5])))
        db.close()
        return return_list

    def projectWizAdd(add_string): #NOT-INCLUDE
        add_string = add_string.replace(' | ','|')
        add_string = add_string.replace('| ','|')
        add_string = add_string.replace(' |','|')
        add_string = add_string.split('|',5)
        if len(add_string) == 6:

            log('ADDING -> '+str(add_string))

            conn = sqlite3.connect('dbs/projects.db')
            db = conn.cursor()
            db.execute('insert into projects values (?,?,?,?,?,?)', add_string)
            conn.commit()
            db.close()

        else:
            return sendMsg(None, 'Syntax: <name> | <version> | <description> | <maintainers> | <lang> | <status>')

    if parsed['event'] == 'privmsg':
        unick = parsed['event_nick']
        message = parsed['event_msg']
        main_trigger = NICK + ", projects"
        if main_trigger in message:
            trigger =  message.replace(main_trigger,'')
            trigger = trigger.split(None, 1)

            if not trigger:
                #help msg here in future
                return sendMsg(None, 'why yes please')

            if trigger[0] == 'add':
                if len(trigger) < 2:
                    return sendMsg(None, 'I should output help messages for add, but I wont')
                return projectWizAdd(trigger[1])
            elif trigger[0] == 'list':
                if len(trigger) < 2:
                    return sendMsg(None, 'Correct syntax: projects list [open|closed|lang] ')
                log('\''+trigger[1]+'\'')
                return projectWizList(trigger[1])
            else:
                return sendMsg(None, 'Proper syntax, learn it!')

def quoteIt(parsed):
    if parsed['event'] == 'privmsg':
        message = parsed['event_msg']
        combostring = NICK + ", quote "
        if combostring in message:
            message = message.split(combostring)[1]
            log("Inside the quoting if!")
            quotation = message
            conn = sqlite3.connect('dbs/quotes.db',isolation_level=None)
            db = conn.cursor()
            name = message.split('>')[0].replace('<','')
            db.execute("INSERT INTO quote (name, quotation) VALUES (?, ?)",[name, quotation])
            conn.close()
            return sendMsg(None, "Quote recorded")

def echoQuote(parsed):
    if parsed['event'] == 'privmsg':
        message = parsed['event_msg']
        combostring = NICK + ", quotes from "
        if combostring in message:
            message = message.split(combostring)[1]
            conn = sqlite3.connect('dbs/quotes.db',isolation_level=None)
            db = conn.cursor()
            quotie = db.execute("SELECT quotation FROM quote WHERE name=? ORDER BY RANDOM() LIMIT 1",[message]).fetchall()
            return_list=[]
            for row in quotie:
                return_list.append(sendMsg(None, "%s" % (row[0])))
            db.close()
            return return_list

def hackerJargons(parsed):
    if parsed['event'] == 'privmsg':
        message = parsed['event_msg']
        main_trigger = NICK + ", jargon"
        if main_trigger in message:
            if authUser(parsed['event_nick']) == True:

                trigger =  message.replace(main_trigger,'')
                trigger = trigger.split(None, 1)
                conn = sqlite3.connect('dbs/jargon.db',isolation_level=None)
                db = conn.cursor()
                jargon = db.execute("SELECT * FROM jargons ORDER BY RANDOM() LIMIT 1").fetchall()
                return_list = []
                for row in jargon:
                    out = list(row)
                    out[0] = out[0].encode("utf-8", "replace")
                    out[1] = out[1].encode("utf-8", "replace")
                    out[2] = out[2].encode("utf-8", "replace")

                    out[2] = out[2].replace('   ','').replace('\r','')
                    j_list = out[2].split('\n')
                    #print out[2]
                    #try:
                    #    irc.send('PRIVMSG '+ str(CHANNEL) +' :' + str(out[2]) + '\r\n')
                    #irc.send('PRIVMSG '+ ' :' + line + '\r\n') #not sure if we need the \r\n
                    #except:
                    #    print 'jargon send failed'
                    return_list.append(sendMsg(None, out[0]+', '+out[1]+' : '))
                    for r in j_list:
                        return_list.append(sendMsg(None, r))
                db.close()
                return return_list

def newReply(parsed):
    if parsed['event'] == 'privmsg':
        message = parsed['event_msg']
        nick = parsed['event_nick']
        combostring = NICK + ", "
        if combostring in message:
            log("nick in msg")
            if '->reply' in message:
                if '->rm' in message:
                    return
                log("->reply in msg")
                message = message.replace(combostring, '')
                try:
                    trigger = message.split('->reply')[0].rstrip()
                    reply = message.split('->reply')[1::]
                    reply = reply[0].lstrip()
                except:
                    return sendMsg(None, 'Incorrect syntax')
                #trigger = trigger.replace(combostring, '')
                conn = sqlite3.connect('dbs/reply.db',isolation_level=None)
                conn.text_factory = str
                db = conn.cursor()
                #replies (trigger text, reply text)
                db.execute("INSERT INTO replies (trigger, reply) VALUES (?, ?)",[trigger, reply])
                db.close()

"""
def trigReply(parsed):
    if parsed['event'] == 'privmsg':
        message = parsed['event_msg']
        nick = parsed['event_nick']
        conn = sqlite3.connect('dbs/reply.db',isolation_level=None)
        conn.text_factory = str
        db = conn.cursor()
        #message = str(message)
        reply = db.execute("SELECT reply FROM replies WHERE trigger=? ORDER BY RANDOM() LIMIT 1",[message]).fetchall()
        return_list = []
        for row in reply:
            return_list.append(sendMsg(None, "%s" % (row[0].replace('$nick',nick))))
        db.close()
        return return_list
"""

def trigReply(parsed):
    if parsed['event'] == 'privmsg':
        global that_was
        message = parsed['event_msg']
        nick = parsed['event_nick']
        what_trigger = NICK + ", what was that?"
        if what_trigger in message:
            if that_was is not None:
                return sendMsg(None, that_was)
            else:
                return sendMsg(None, 'what was what?')
        conn = sqlite3.connect('dbs/reply.db',isolation_level=None)
        conn.text_factory = str
        db = conn.cursor()
        returned = ''
        #message = str(message)
        reply = db.execute("SELECT reply FROM replies WHERE trigger=? ORDER BY RANDOM() LIMIT 1",[message]).fetchall()
        if len(reply) > 0:
            return_list = []
            for row in reply:
                return_list.append(sendMsg(None, "%s" % (row[0].replace('$nick',nick))))
                returned = row[0].replace('$nick',nick)
            db.close()
            that_was = '"'+returned+'" triggered by "'+message+'"'
            return return_list
        else:
            return

def rmReply(parsed):
    if parsed['event'] == 'privmsg':
        message = parsed['event_msg']
        nick = parsed['event_nick']
        combostring = NICK + ", "
        if combostring in message:
            #print "nick in msg"
            if '->rm' in message:
                log("->rm in msg")
                try:
                    reply = message.split('->rm')[1].lstrip()
                except:
                    return sendMsg(None, 'Incorrect syntax')
                conn = sqlite3.connect('dbs/reply.db',isolation_level=None)
                conn.text_factory = str
                db = conn.cursor()
                #replies (trigger text, reply text)
                if authUser(nick) == True:
                    db.execute("DELETE FROM replies WHERE reply=?",[reply])
                    return_msg = sendMsg(None, "Total records deleted: " + str(conn.total_changes))
                else:
                    return_msg = sendMsg(None, "03>Lol nice try faggot")
                db.close()
                return return_msg

def intoLines(parsed):
    if parsed['event'] == 'privmsg':
        message = parsed['event_msg']
        nick = parsed['event_nick']
        conn = sqlite3.connect('dbs/lines.db',isolation_level=None)
        conn.text_factory = str
        db = conn.cursor()
        reply = db.execute("INSERT INTO lines (name, message) VALUES (?, ?)",[nick, message])
        db.close()

def spewLines(parsed):
    if parsed['event'] == 'privmsg':
        message = parsed['event_msg']
        nick = parsed['event_nick']
        combostring = NICK + ", spew like "
        if combostring in message:
            name = message.replace(combostring, '')
            name = name.strip()
            conn = sqlite3.connect('dbs/lines.db',isolation_level=None)
            conn.text_factory = str
            db = conn.cursor()
            reply = db.execute("SELECT message FROM lines WHERE name=? ORDER BY RANDOM() LIMIT 1",[name]).fetchall()
            return_list = []
            for row in reply:
                return_list.append(sendMsg(None, "%s" % (row[0])))
            db.close()
            return return_list

def Greeting(parsed):
    if parsed['event'] == 'privmsg':
        combostring = NICK + ", greet "
        message = parsed['event_msg']
        if combostring in message:
            if authUser(parsed['event_nick']) == True:
                name = message.replace(combostring, '').split(' ',1)[0]
                name = name.strip()
                if len(name) < 1:
                    return sendMsg(None, 'who?')
                if parsed['event_nick'] == name:
                    return sendMsg(parsed['event_nick'], 'u silly poophead')
                try:
                    msg = message.replace(combostring, '').split(' ',1)[1]
                except:
                    return sendMsg(None, 'how?')
                if authUser(name) == True:
                    conn = sqlite3.connect('dbs/greetings.db',isolation_level=None)
                    conn.text_factory = str
                    db = conn.cursor()
                    reply = db.execute("SELECT greeting FROM greetings WHERE nick=?",[name]).fetchall()
                    if len(reply) > 0:
                        db.close()
                        return sendMsg(None, 'I already greet '+name+' with, '+reply[0][0])
                    else:
                        db.execute("INSERT INTO greetings (nick, greeting) VALUES (?, ?)",[name, msg])
                        db.close()
                        return sendMsg(None, 'will do')
                else:
                    return sendMsg(None, 'I only greet GODS, so..')
    if parsed['event'] == 'privmsg':
        combostring = NICK + ", don't greet "
        message = parsed['event_msg']
        if combostring in message:
            if authUser(parsed['event_nick']) == True:
                name = message.replace(combostring, '')
                conn = sqlite3.connect('dbs/greetings.db',isolation_level=None)
                conn.text_factory = str
                db = conn.cursor()
                db.execute("DELETE FROM greetings WHERE nick=?",[name])
                db.close()
                return sendMsg(None, 'okay.. ;_;')
    if parsed['event'] == 'join':
        if authUser(parsed['event_nick']) == True:
            name = parsed['event_nick']
            conn = sqlite3.connect('dbs/greetings.db',isolation_level=None)
            conn.text_factory = str
            db = conn.cursor()
            reply = db.execute("SELECT greeting FROM greetings WHERE nick=?",[name]).fetchall()
            db.close()
            if len(reply) > 0:
                time.sleep(2)
                return sendMsg(name, reply[0][0])

def Colors(parsed):
    if parsed['event'] == 'privmsg':
        combostring = NICK + ", add color "
        message = parsed['event_msg']
        if combostring in message:
            color = message.replace(combostring, '').split(' ',1)
            if len(color) == 2:
                hex_test = re.search('#([0-9A-Fa-f]{6})', color[0])
                if hex_test is not None:
                    hex_test = hex_test.group()
                    hex_test = hex_test.strip('#')
                    r = int(hex_test[0:2], 16)
                    g = int(hex_test[2:4], 16)
                    b = int(hex_test[4:7], 16)
                    conn = sqlite3.connect('dbs/colors.db',isolation_level=None)
                    conn.text_factory = str
                    db = conn.cursor()
                    db.execute("INSERT INTO colors (r,g,b, colorname) VALUES (?, ?, ?, ?)",[r, g, b, color[1]])
                    db.close()
                    log('Added a color definition')
                    return sendMsg(None, 'Added a color definition')
                else:
                    return sendMsg(None,'SYNTAX: add color #ffffff definition')
            else:
                return sendMsg(None,'SYNTAX: add color #ffffff definition')
        uname = re.search('#([0-9A-Fa-f]{6})', parsed['event_msg'])
        if uname is not None:
            uname = uname.group()
            log(uname+' seen')
            uname = uname.strip('#')
            r = int(uname[0:2], 16)
            g = int(uname[2:4], 16)
            b = int(uname[4:7], 16)
            conn = sqlite3.connect('dbs/colors.db',isolation_level=None)
            conn.text_factory = str
            db = conn.cursor()
            reply = db.execute("SELECT colorname FROM colors WHERE r=? AND g=? AND b=? ORDER BY RANDOM() LIMIT 1",[r, g ,b]).fetchall()
            db.close()
            return_list = []
            if len(reply) > 0:
                return_list.append(reply[0][0])
            else:
                return_list.append('I haven\'t heard about that color before.')
            if authUser(parsed['event_nick']) == True:
                os.system('convert -size 100x100 xc:#%s mod_colors.png' % (uname))
                fin,fout = os.popen4('./mod_colors.sh mod_colors.png')
                return_list.append(' => ')
                for result in fout.readlines():
                    return_list.append(result)
                    log(result)
                return_list = ''.join(return_list)
            return sendMsg(None, return_list)