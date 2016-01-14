# the-silencer
A slow post DoS/stress testing tool based upon torshammer

Improved by changing content length and keep alive to a little smaller but seemingly random value, which will prevent the detection based on the requests that Torshammer sent.

More improvements will be made over time.

Check out my blog! http://zunzutech.com/blog

Check out my forum! http://zunzutech.com/forum

Planned features: Stopping the attack after the server is down prevent malicious uses which will use isup.me to check. Maybe try to make it more efficient, and give it the ability of cookies and javascript because sometimes firewalls block silencer.



THIS IS MADE SOLELY FOR STRESS TESTING PURPOSE, ANY USE OF THIS TOOL FOR MALICIOUS PURPOSES, INCLUDING BUT NOT LIMITED TO DOS, DDOS, TAKING DOWN A SITE, OR USING IT ON A SITE WITHOUT THE OWNER'S PERMISSION IS PROHIBITED. I AM NOT LIABLE TO ANYTHING YOU DO WITH THIS TOOL/CODE/SCRIPT.

Usage example:

./the-silencer-master/thesilencer.py -t target.com -r 100 -p 80 -T

This will send the stress test to target.com with 100 threads, on port 80, and the test will run through the Tor network. You can leave out the -p and -r, by default the number of threads is 256 and the port is 80. If you leave out -T then the attack will come directly from you to the server and not through Tor.


