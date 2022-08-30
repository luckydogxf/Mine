#!/usr/bin/env python2.6
#
# http://docs.python.org/library/imaplib.html

USERNAME="hfu@xxx.com"
PASSWORD="VERY_SECURE_PWD"
EMAIL_KEEP_DAYS= 3# delete all emails before ( today - 3 days )

import time, datetime
import imaplib, string, email
import re, sys

M = imaplib.IMAP4_SSL("imap.collaborationhost.net")
date = (datetime.date.today() - datetime.timedelta(EMAIL_KEEP_DAYS)).strftime("%d-%b-%Y")

def extract_mail(string):
    mails =[]
    email_pattern = re.compile('<([\w\-\.]+@(\w[\w\-]+\.)+[\w\-]+)>')
    for match in email_pattern.findall(string):
        mails.append(match[0])

    str = ','.join(list(set(mails)))
    return str.lower()

M.login(USERNAME, PASSWORD)

result, message = M.select()
# http://www.example-code.com/asp/imap-search-examples.asp
type, data = M.search(None, '(SENTBEFORE {date})'.format(date=date))
print data
i = 0
for num in string.split(data[0]):
    try:
        type, data = M.fetch(num, '(RFC822)')
    except imaplib.abort:
        print "EOF"
        break
    msg = email.message_from_string(data[0][1])


    # mid = msg["Thread-Index"]
    # sender = extract_mail(msg["From"])
    # recipient = extract_mail(msg["To"])
    newtime = ""
    if "Date" in msg:
        newtime = msg["Date"].replace(' -0600','').replace(' -0500', '')
        print newtime
        #sdate = time.mktime(time.strptime(newtime, "%a, %d %b %Y %H:%M:%S"))

    print "deleting: ", i, num, newtime, msg['Subject']
    M.store(num, '+FLAGS', '\\Deleted')

    M.expunge()

M.expunge()
M.close()
M.logout()


