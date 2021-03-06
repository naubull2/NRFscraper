import sys
import signal
import requests
import schedule
import pickle
import re
import time
import smtplib

from email.mime.text import MIMEText
from lxml import html
from os.path import isfile

HOST_NAME = 'lime'
SCRAP_TIME = '18:00'
BACKUP_PKL = 'NRF.pkl'
new_assignments = set() 

def job(links):
    # check for assignmnets uploaded today
    global new_assignments

    assignments = []
    for link in links:
        page = requests.get(link)
        tree = html.fromstring(page.content)

        date_today = time.strftime('%Y-%m-%d')
        """ Add the specific crawling codes for other
            notification boards you want to check 
        """
        if 'nrf' in link:
            dates = tree.xpath('//td[@width="8%"]/text()')
            titles = map(lambda x: x.strip(), 
                    tree.xpath('//a[@class="bd_text_ov"]/text()'))

            # keep the assignments uploaded today
            assignments = [(title, date, link) 
                    for title, date in zip(titles, dates) 
                                     if date == date_today] 
            print('Checked NRF')
        elif 'rndgate' in link:
            titles = map(lambda x: x.strip(), 
                    tree.xpath('//td[@class="left"]/a/text()'))

            date_pattern = re.compile('[0-9]{4}.[0-9]{2}.*')
            dates = [date.replace('.', '-') for date in tree.xpath('//td/text()') 
                                                if date_pattern.match(date)]

            assignments = [(title, date, link)
                    for title, date in zip(titles, dates)
                                      if date == date_today]
            print('Checked RNDgate')
        elif 'iitp' in link:
            # duplicates should be counted so the dates will not be skewed
            titles = map(lambda x: x.strip(),
                    tree.xpath('//td[@class="no-space comment-group"]/a/text()'))
            titles0 = map(lambda x: x.strip(), 
                    tree.xpath('//td[@class="no-space comment-group0"]/a/text()'))

            date_pattern = re.compile('[0-9]{4}-[0-9]{2}-*')
            dates = [date for date in tree.xpath('//td[@class="text-center"]/text()') 
                              if date_pattern.match(date)]
            titles.extend(titles0)

            assignments = [(title, date, link)
                    for title, date in zip(titles, dates)
                              if date == date_today]
            print('Checked IITP')
        elif 'etri' in link:
            titles = map(lambda x: x.strip(),
                    tree.xpath('//div[@class="text_one_line"]/a/text()'))
            date_pattern = re.compile('[0-9]{4}-[0-9]{2}-*')
            dates = [date for date in tree.xpath('//td/text()')
                              if date_pattern.match(date)]

            # ETRI board contain both application init & end dates
            # We only want the init dates
            assignments = [(title, date, link)
                    for title, date in zip(titles, dates[::2])
                              if date == date_today]
            print('Checked ETRI')
        elif 'snurnd' in link:
            titles = map(lambda x: x.strip(),
                    tree.xpath('//td[@class="subject"]/a/text()'))
            dates = tree.xpath('//td/text()')
            date_pattern = re.compile('[0-9]{4}.[0-9]{2}.*')
            dates = [date.replace('.', '-') for date in dates
                                                if date_pattern.match(date)]
            assignments = [(title, date, link)
                    for title, date in zip(titles, dates)
                                      if date == date_today]
            print('Checked SNU RND')
        if len(assignments) > 0:
            print('There are some new notifications!')
        else:
            print('Nothing new!')
        # add any new assignments
        for assign in assignments:
            new_assignments.add(assign)

def notify(host_addrs, to_whom):
    # send an email containing a list of new assignments
    global new_assignments

    # create message for the responsible members from the user list
    FROM = host_addrs 
    today_is = time.strftime('%d')
    TO = []
    if type(to_whom) is list:
        for date, user_mail in to_whom:
            if today_is == date:
                TO.append(user_mail)
    else:
        TO.append(to_whom)
    SUBJECT = '[Research fund notification]'
    if len(new_assignments) == 0:
        TEXT = 'Nothing to report!'
        return
    else:
        TEXT = '\n\n'.join(map(lambda x: '[%s]\t%s\n%s' % (x[1], unicode(x[0]), x[2]),
                             map(list, new_assignments)))

    server = smtplib.SMTP(host='your.smtp.server', port=25)
    #server.set_debuglevel(1)
    server.starttls()
    # only send if the receivers are designated
    if TO:
        message = MIMEText(TEXT, 'plain', 'utf-8')
        message['Subject'] = SUBJECT
        message['From'] = FROM
        message['To'] = ','.join(TO)
        server.sendmail(FROM, TO, message.as_string())

        # clear list
        new_assignments.clear()
        print("Sent a mail to {}".format(TO))

    server.quit()

def signal_handler(signal, frame):
    # save the set of new titles in a file
    global new_assignments
    pickle.dump(new_assignments, open(BACKUP_PKL, 'wb'))
    sys.exit(0)

if __name__=='__main__':
    if len(sys.argv) < 2:
        print('Usage: python [%s] [%s] [%s]' 
                % ('a file of links to check',
                   'time in HH:MM format',
                   'an email address to send notification to'))
        print('  - Time format is in 24hr, e.g., 13:30')
        exit()
    signal.signal(signal.SIGINT, signal_handler)

    links = []
    with open(sys.argv[1], 'r') as f:
        links = [line.strip() for line in f]

    if isfile(BACKUP_PKL):
        new_assignments = pickle.load(open(BACKUP_PKL, 'rb'))
     

    # The timer format is "hh:mm"
    timed_at = sys.argv[2]
    to_whom = sys.argv[3]
    users = []
    if to_whom.rsplit('.',1)[-1] == 'txt':
        with open(to_whom, 'r') as f:
            for line in f:
                date, mail = line.strip().split()
                users.append((date, mail))
        schedule.every().day.at(timed_at).do(notify, HOST_NAME, users)
    else:
        schedule.every().day.at(timed_at).do(notify, HOST_NAME, to_whom)
    schedule.every().day.at(SCRAP_TIME).do(job, links)
    print('Scheduled to notify to %s at %s everyday!'
                            % (to_whom, timed_at))

    while True:
        schedule.run_pending()
        time.sleep(30)
