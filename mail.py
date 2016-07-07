import smtplib

def prompt(prompt):
    return raw_input(prompt).strip()

fromaddr = "toputop@toputopu.com"
toaddrs  = "johnnysangel@163.com"
print "Enter message, end with ^D (Unix) or ^Z (Windows):"

# Add the From: and To: headers at the start!
msg = "Message"

print "Message length is " + repr(len(msg))

server = smtplib.SMTP('localhost')
server.set_debuglevel(1)
server.sendmail(fromaddr, toaddrs, msg)
server.quit()
