#!/usr/bin/env python

import os,sys,pexpect,time

fortimail = ['172.16.232.100']

user="admin"
# Change it accordingly when you change FML's admin password.
passwd="BnRsldsxz@sd^*q7gt"
base="/etc/letsencrypt/live/pt/"

# CLI
with open(base + 'cert.pem') as f1, open(base + 'privkey.pem') as f2:
   certificate = f1.read()
   key = f2.read()

config_cert_cli='config system certificate local\nedit Free_cert\nset password ""\nset private-key \"%s\"\nset certificate \"%s\"\nset comments Lets_Encrypt\nend\nconfig system global\nset default-certifi
cate Free_cert\nend\n' %(key, certificate)

def cert_config(ip) :
      try:
        ssh = pexpect.spawn('ssh %s@%s ' % (user,ip), timeout=120)
        i = ssh.expect(['(?i)Password','continue connecting (yes/no)?','[$#>]','No route to host','pexpect.TIMEOUT'])

        if i == 0:
             ssh.sendline(passwd)

        elif i == 1:
             ssh.sendline('yes')
             ssh.expect('Password')
             ssh.sendline(passwd)

        elif i == 2:
             ssh.sendline()

        elif i == 3:
             print 'couldn\'t connect to host ', ssh.before

        else :
             print 'ssh to host timeout ,please check network and pasword'

        ssh.expect('[$#>]')
        #ssh.logfile_read = sys.stdout
        ssh.sendline(config_cert_cli)
        # wait for a while to take effect.
        time.sleep(15)
        # User's Home, /root
        f = open('/tmp/' + ip , "w")
        ssh.logfile_read = f
        ssh.expect('[>$#]')
        ssh.sendline('exit')
        # without EOF, buffer probably won't flush into file.
        ssh.expect(pexpect.EOF)
        f.close()

      except Exception,e :
          f.close()
          ssh.close()
          print " connect error,",str(e)
          sys.exit(1)


for i in fortimail:
    cert_config(i)

