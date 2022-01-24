import os.path
import urllib.request
import urllib.error
import ssl
import re
import datetime
import util
import colorama
from colorama import Fore
colorama.init(autoreset=True)
# files
data_dir = os.getcwd() 
feeds_file = os.path.join(data_dir, 'news.csv') 
users_file = os.path.join(data_dir, 'users.csv') 
WIDTH = 150 
URL = "http://rss.in.gr/" 
user = {} 
#user = {'user': 'nikos', 'areas': {'Ειδήσεις Πολιτισμός': ['Καζαντζάκη'], 'Υγεία': []}
acceptable_answers = ['NAI','ΝΑΙ','Ν','N','OXI','ΟΧΙ','O','Ο']

def login_user():
    global user
    flag = False
    while True:
        username=input("Username: ")
        if username== '':break
        if re.findall(r'^\w+?\b$',username):
            if username == 'admin':
                flag=True
                admin()
            else:
                if retrieve_user(username):
                    print(Fore.BLUE+f"\nΚαλωσόρισες {username}!")
                    flag=True
                    break
                else:
                    answer = ''
                    while not answer.upper() in acceptable_answers:
                        answer=input("Δεν υπάρχει χρήστης με το όνομα που δώσατε, θέλετε να δημιουργήσετε το προφίλ σας; (ΝΑΙ/ΟΧΙ)")
                        if answer.upper() in acceptable_answers[:4]:
                            user={'user':username, 'areas':{}}
                            update_user()
                            flag=True
                        break
                    break
        else:
            print(Fore.RED+"\n(!) Το όνομα χρήστη πρέπει να είναι μια λέξη χωρίς σύμβολα η ειδικούς χαρακτήρες")
    return flag


def admin():
    while True:
        users_from_file=util.csv_to_dict(users_file)
        temporary_users=[]
        for row in users_from_file:
            if not row['user'] in temporary_users:
                temporary_users.append(row['user'])
        print("\nΟι χρήστες είναι: ")
        for user in temporary_users:
            print(f"\t\t{user}")

        print("\nΔΙΑΧΕΙΡΗΣΗ ΧΡΗΣΤΩΝ:")
        print("\t+χρήστη: για δημιουργία νέου χρήστη \t(+Νικος θα δημιουργήσει τον χρήστη Νικο)")
        print("\t-χρήστη: για διαγραφή υπάρχοντα χρήστη \t(-Νικος θα διαγράψει τον χρήστη Νικο)")

        input_user=input("\t").split()
        if len(input_user)==0:break
        for user in input_user:  
            if re.findall(r'^[\-\+]\w+?\b',user):
                if '+' == user[0]:
                    user=user[1:]
                    if user in temporary_users:
                        print(Fore.RED+f"\n(!) Ο χρήστης {user} υπάρχει ήδη")
                    else:
                        users_from_file.append({'user': user, 'areas': '', 'keywords': ''})       
                else:
                    user=user[1:]
                    if not user in temporary_users:
                        print(Fore.RED+f"\n(!) Ο χρήστης {user} δεν υπάρχει")
                    else:
                        answer=''
                        while not answer.upper() in acceptable_answers:
                            answer=input(f"Θέλεις να διαγράψεις το προφίλ του χρήστη {user}; (ΝΑΙ/ΟΧΙ) ")
                            if answer.upper() in acceptable_answers[:4]:
                                temp_users=[]
                                for row in users_from_file:
                                    if user != row['user']:
                                        temp_users.append(row)
                                users_from_file=temp_users
            else: print(Fore.RED+"\n(!) Προσθέστε νέο χρήστη με '+' μπροστά από το όνομα του, η '-' για να τον διαγράψετε.")
            
        util.dict_to_csv(users_from_file, users_file)

def retrieve_user(username): 
    global user
    users_from_file=util.csv_to_dict(users_file)
    areas={}
    flag=0
    for row in users_from_file:
        if row['areas']:
            temp_list=['']
            if row['user'] == username:
                flag=1
                if re.findall('\$',row['keywords']):
                    temp_list=row['keywords'].split('$')
                else:
                    temp_list[0]=row['keywords']
                areas[row['areas']]=temp_list
    if flag:
        user={'user':username, 'areas':areas}
        return True
    else: 
        return False   


def update_user(): 
    global user
    users_from_file=util.csv_to_dict(users_file)
    temp_list=[]
    for row in users_from_file:
        if user['user'] != row['user']:
            temp_list.append(row)
    users_from_file=temp_list
    if not user['areas']:
        users_from_file.append({'user': user['user'], 'areas': '', 'keywords': ''})
    else:
        for subject,keywords in user['areas'].items():
            keywords_string="$".join(keywords)
            users_from_file.append({'user': user['user'], 'areas': subject, 'keywords': keywords_string})
    util.dict_to_csv(users_from_file, users_file)

def load_newsfeeds():
    if os.path.isfile(feeds_file) :
        return util.csv_to_dict(feeds_file)
    else:
        print(Fore.RED+f'\n(!) Δεν υπάρχει αρχείο {feeds_file}\n')
        return False

def load_news_to_temp(feeds):
    count = 0
    news_items = []
    for area in user['areas']:
        print(area, ' ....', end='')
        url = [x['rss'] for x in feeds if x['title'] == area]
        try:
            ctx = ssl.create_default_context()
            ctx.set_ciphers('DEFAULT@SECLEVEL=1')
            with urllib.request.urlopen(url[0], context=ctx) as response:
                html = response.read().decode()
            filename = "tempfile.rss"
            with open(filename, "w", encoding="utf-8") as p:
                p.write(html)
        except urllib.error.HTTPError as e:
            print(e.code)
            print(e.readline())
        except urllib.error.URLError as e:
            print(e)
            if hasattr(e, 'reason'):  # χωρίς σύνδεση ιντερνετ
                print('Αποτυχία σύνδεσης στον server')
                print('Αιτία: ', e.reason)
        else:
            with open(filename, 'r', encoding='utf-8') as f:
                rss = f.read().replace("\n", " ")
                items = re.findall(r"<item>(.*?)<\/item>", rss, re.MULTILINE | re.IGNORECASE)
                count_area_items = 0
                for item in items:
                    news_item = {}
                    title = re.findall(r"<title>(.*?)<\/title>", item, re.MULTILINE | re.IGNORECASE)
                    date = re.findall(r"<pubdate>(.*?)<\/pubdate>", item, re.MULTILINE | re.IGNORECASE)
                    link = re.findall(r"<link>(.*?)<\/link>", item, re.MULTILINE | re.IGNORECASE)
                    if len(title) > 0:
                        title = title[0]
                    else: 
                        title = ''
                    date = format_date(date[0]) if date else ' '
                    content = re.findall(r"<\/div\>(.*?)\]\]\>", item, re.MULTILINE | re.IGNORECASE)
                    found = False
                    if user['areas'][area]:
                        for k in user['areas'][area]:
                            if check_keyword(k, title) or check_keyword(k, content[0]):
                                found = True
                                break
                            else: 
                                found = False
                    else:
                        found = True
                    if found:
                        count += 1
                        count_area_items += 1
                        news_item = {'no':count, 'title': title, 'date':date, 'content': content[0]+f" \n(link: {link[0]})"}
                        news_items.append(news_item)
                        if count> 99: break # μόνο 100 πρώτες ειδήσεις
            print(count_area_items, end= ' ,   ')
    util.dict_to_csv(news_items, 'mytemp.csv') # temporary store of news items
    print()
    return len(news_items)

def print_titles():

    try:
        news_items = util.csv_to_dict('mytemp.csv')
        for item in news_items:
            print(item['no'] + '\t[' + item['date'] + ']\t' + item['title'])
        return True
    except FileNotFoundError:
        return False

def print_news_item(item_no):

    file=util.csv_to_dict('mytemp.csv')
    for x in file:
        if item_no == int(x['no']):
            # print((f"\n{x['no']}) [{x['date']}]  {x['title']}\n"))
            formatted_print((f"\n{x['no']}) [{x['date']}]  {x['title']}\n"))
            # print(x['content'])
            formatted_print(x['content'])
            return True
    return False


def format_date(date):
    m_gr = 'Ιαν Φεβ Μαρ Απρ Μαϊ Ιουν Ιουλ Αυγ Σεπ Οκτ Νοε ∆εκ'.split()
    m_en = 'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split()
    d = re.findall(r"([0-9]{2}\s[A-Z][a-z]{2}\s[0-9]{4})",date, re.I)
    if d : date = d[0].split()
    if date[1] in m_en: date[1] = m_gr[m_en.index(date[1])]
    return ' '.join(date)


def check_keyword(keyword, text):
    tonoi = ('αά', 'εέ', 'ηή', 'ιί', 'οό', 'υύ', 'ωώ')
    new_phrase= ''
    for c in keyword:
        char = c
        for t in tonoi:
            if c in t: char = '['+t+']'
        new_phrase += char
    pattern = r'.*'+new_phrase+r'.*'
    found =re.findall(pattern, text, re.I)
    if found:
        return True
    else:
        return False

def formatted_print(text, width=WIDTH):
    lines = text.split("\n")
    for line in lines:
        output=""
        if len(line)>width:
            words = line.split(" ")
            for index,word in enumerate(words):
                if not len(output+" "+word)>width:
                    output+=word+" "
                else:
                    print(output)
                    output=word+" "
        else:
            output=line
        print(output)

def manage_profile(feeds):
    global user
    modify = False
    dicf={}
    c=0
    while True:
        print_user_profile()
        print(WIDTH * '_')
        reply = input('Θέλετε να αλλάξετε το προφίλ σας; (Ναι για αλλαγές)')
        if not reply or reply[0].lower() not in 'νn': break
        print('Αρχικά θα μπορείτε να επιλέξετε από θέματα ειδήσεων, στη συνέχεια να ορίσετε όρους αναζήτησης σε καθένα από αυτά')
        main_feeds = [x['title'] for x in feeds ]

        for x in main_feeds:
            print(x)
        
        ke=[]
        dicu=user['areas']
        for x in feeds:
            i=re.findall(r"{'title': '(.*?)', 'rss'",str(x))
            dicf[c]=i[0]
            c+=1
        while True:
            print('\nΤα κύρια θέματα ειδήσεων είναι: ....')
            print('\nID -  Τίτλος')                 
            print('------------------')                 
            for x in dicf:
                print(x," - ",dicf[x])
            inuser=input("\nΜπορείτε να προσθέστε θέμα με +ID ή να αφαιρέσετε με -ID (enter για να συνεχίσετε): ").split()
            if inuser==[]:break
            for y in inuser:
                if re.findall(r'^[-+]\d+?$', y):
                    modify = True
                    if '+' in y:
                        numb=int(re.sub('[-+]','', y))
                        epil=dicf[numb]
                        dicu=user['areas']
                        try:
                            del dicu['']
                            dicu[epil]=ke
                            user['areas']=dicu
                        except:
                            dicu[epil]=ke
                            user['areas']=dicu
                    else:
                        numb=int(re.sub('[-+]','', y))
                        epil=dicf[numb]
                        dicu=user['areas']
                        try:
                            del dicu[epil]
                            user['areas']=dicu
                        except:
                            print('Το θέμα ειδήσεων {} δεν υπάρχει στα επιλεγμένα θέματα σας'.format(epil))
            xe=re.findall(r"dict_keys\(\['(.*?)\]\)",str(user['areas'].keys()))
            endiaf=', '.join(xe)
            endiaf=re.sub("\'","",endiaf)
            print(Fore.GREEN+'\nΤα ενδιαφέροντά σας είναι ... ',endiaf)

        print_user_profile()
        print('\nΤώρα για κάθε θέμα ειδήσεων μπορείτε να επιλέξετε όρους αναζήτησης')

        for x in dicu:
            a=[]
            for y in dicu[x]:
                a.append(y)
            while True:
                print("\nΘΕΜΑ:  {}  .. Όροι αναζήτησης: {}\n".format(x,a))
                inuser=input("\nΜπορείτε να προσθέσετε ή να αφαιρέσετε όρους για κάθε θέμα με +λέξη, -λέξη....(enter για να συνεχίσετε): ").split()                    
                if inuser==[]:break
                for o in inuser:
                    if re.findall(r'^[-+]\w+?$', o):
                        modify = True
                        if '+' in o:
                            word=re.sub('[-+]','', o)
                            a.append(word)
                        else:
                            word=re.sub('[-+]','', o)
                            if not word in a:
                                print("Δεν υπάρχει η λέξη {}".format(word))
                            else:
                                a.remove(word)
            dicu[x]=a     
        user['areas']=dicu

        print_user_profile()
        reply = input('\n ... Θέλετε άλλες αλλαγές στο προφίλ σας (ναι για αλλαγές))')
        if not reply or reply[0].lower() != 'ν': break
    if modify:
        update_user()


def print_user_areas(li):
    print('\nΤα ενδιαφέροντά σας είναι ...', end='')
    items = False
    for item in li:
        if item in user['areas'].keys():
            print(item, end=', ')
            items = True
    if not items: print('ΚΑΝΕΝΑ ΕΝΔΙΑΦΕΡΟΝ', end='')
    print()

def print_user_profile():
    print('\nΤα θέματα ειδήσεων που σας ενδιαφέρουν είναι:')
    if not user['areas']: print('KENO ΠΡΟΦΙΛ ΧΡΗΣΤΗ')
    for area in user['areas']:
        print(area)
        for keyword in user['areas'][area]:
            print('\t\t', keyword)

def clear_temps():

    if os.path.isfile('tempfile.rss'):
        os.remove('tempfile.rss') 
    if os.path.isfile('mytemp.csv'):
        os.remove('mytemp.csv')
    if os.path.isdir('__pycache__'):
        try:
            os.rmdir('__pycache__')
        except:
            p=os.listdir('__pycache__')
            for i in p:
                j=os.path.join('__pycache__',i)
                os.remove(j)
            os.rmdir('__pycache__')    

def main():
    print("Σήμερα είναι :", str(datetime.datetime.today()).split()[0])
    username = login_user()
    if username:
        feeds = load_newsfeeds()
        if feeds:
            print('\nTo mynews πρoσφέρει προσωποποιημένες ειδήσεις από το in.gr')
            while True: # main menu
                print(WIDTH * '=')
                user_selected = input('(Π)ροφίλ ενδιαφέροντα, (Τ)ίτλοι ειδήσεων, (enter)Εξοδος\n')
                if user_selected == '': # έξοδος
                    break
                elif user_selected.upper() in 'ΠP': # προφίλ
                    manage_profile(feeds) # διαχείριση του προφίλ χρήστη
                elif user_selected.upper() in 'ΤT': # παρουσίαση τίτλων ειδήσεων
                    if 'areas' in user.keys() and len(user['areas']) > 0 : # αν ο χρήστης έχει ορίσει areas
                        print_user_profile()
                        print('\nΤΕΛΕΥΤΑΙΕΣ ΕΙΔΗΣΕΙΣ ΠΟΥ ΣΑΣ ΕΝΔΙΑΦΕΡΟΥΝ...ΣΕ ΤΙΤΛΟΥΣ')
                        items_count = load_news_to_temp(feeds)  # φόρτωσε τις ειδήσεις που ενδιαφέρουν τον χρήστη
                        if items_count: # εαν υπάρχουν ειδήσεις σύμφωνα με το προφιλ του χρήστη ...
                            print_titles() # τύπωσε τους τίτλους των ειδήσεων του χρήστη
                            while True:
                                print(WIDTH * '_')
                                item_no = input(f'Επιλογή είδησης (1 .. {items_count}) ή <enter> για να συνεχίσετε:')
                                if item_no == '': break
                                if item_no.isdigit() and 0 < int(item_no) <= items_count:
                                    print_news_item(int(item_no))
                                else:
                                    print(Fore.RED+f"\n(!) Δώστε έναν αριθμό απο το 1 μέχρι {items_count}.")
                        else: print('Δεν υπάρχουν ειδήσεις με βάση το προφίλ ενδιαφερόντων σας ...')
                    else: print('Πρέπει πρώτα να δημιουργήσετε το προφίλ σας')
    clear_temps()
    print('\nΕυχαριστούμε')


if __name__ == '__main__': main()
