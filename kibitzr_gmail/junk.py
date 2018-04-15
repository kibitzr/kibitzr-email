import imaplib
import email
import email.Header


GMAIL_SSL_HOST = 'imap.gmail.com'

mail = imaplib.IMAP4_SSL(imap_ssl_host, imap_ssl_port)
mail.login('peterdemin@gmail.com', 'Pr1m@rym@1lb0x')
mail.list()
# Out: list of "folders" aka labels in gmail.
mail.select("inbox") # connect to inbox

result, inbox_data = mail.uid('search', None, "ALL") # search and return uids instead
email_uids = inbox_data[0].split()
latest_email_uid = email_uids[-1]
result, body_data = mail.uid('fetch', latest_email_uid, '(RFC822)')
raw_email = data[0][1]

for uid in email_uids:
    result, body = mail.uid('fetch', uid, '(RFC822)')
    raw_email = body[0][1]
    msg = email.message_from_string(raw_email)
    print('%-8s: %s' % ('UID', uid))
    for header in [ 'subject', 'to', 'from' ]:
        #print(msg[header])
        #print(email.Header.decode_header(msg[header]))
        text = email.Header.decode_header(msg[header].replace('\r\n', ' '))[0][0]
        print('%-8s: %s' % (header.upper(), text))
    print('')


 
# print email.utils.parseaddr(email_message['From']) # for parsing "Yuji Tomita" <yuji@grovemade.com>
 
def get_first_text_block(email_message_instance):
    maintype = email_message_instance.get_content_maintype()
    if maintype == 'multipart':
        for part in email_message_instance.get_payload():
            if part.get_content_maintype() == 'text':
                return part.get_payload()
    elif maintype == 'text':
        return email_message_instance.get_payload()


result, body = mail.uid('fetch', '33760', '(RFC822)')
msg = email.message_from_string(body[0][1])
print(get_first_text_block(msg))
