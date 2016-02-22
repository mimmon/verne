#!/usr/bin/python
# -*- coding: cp1250 -*-

## BIO-MARKET
## VERNE-OSTNY SYSTEM / LOYALTY SYSTEM
## 

## records the purchases of the regular customers
## when they reach 50 points (50 eur cumulative purchases)
## they can apply for 10% discount (or whatever benefit).
## When benefit/discount applied, this purchases does not count
## to the total.
## You can
## * record a new user (the id is 8byte number barcode recommended),
## * edit an existing user (except id)
## * add a purchase to customer
## * apply discount (in this case we enter the discounted price for a record)
##
## THINGS TO DO
## version 0.2 writes data to three txt files, it's backed up with every
## operation, but the next versions should
## - use sqlite database for customers and purchases
## - do regular automated backups (each 15 minutes for instance)
## - send email with database back up once in a while (once a day for instance)
## - (far future) send email to customer when get new points or send email once
## in a while (3 months?) in case they have enough points for discount
## - - this may require new value in database of customers - alst day contacted
## - - or also a day when 50 points achieved

import os
import shutil
import sys
import time
import codecs
import re
from datetime import datetime
from tkinter import Tk, Button, Frame
from tkinter import StringVar, Entry, Label

from tkinter.messagebox import askokcancel, showwarning, showinfo

dirname = os.getcwd()

usersFileName = 'users.ver'
purchaseFileName = 'purchases.ver'
logFileName = 'log.ver'

# LIMIT FOR CUSTOMER TO GET A DISCOUNT
limit = 50.

# COLOR SCHEME
# http://wiki.tcl.tk/37701
bgcolor = 'lightgoldenrod' # normal
bgcolor1 = 'DarkOliveGreen1' # background color of ADD_USER
bgcolor2 = 'light coral'
bgcolor3 = 'dark turquoise'  # EDIT_USER
bgcolor4 = 'orange red'
bgcolor5 = 'NavajoWhite3'
fgcolor1 = 'black'
fgcolor2 = 'red'
buttoncolor = 'goldenrod1'
buttoncolor1 = 'DarkOliveGreen3'
buttoncolor3 = 'dodger blue'
buttoncolor4 = 'bisque2'
buttoncolor5 = 'dark orange'
entrycolor = 'cornsilk'
entrycolor1 = 'honeydew'
entrycolor3 =  'pale turquoise'
labelbgcolor = bgcolor
labelbgcolor1 = bgcolor1
statuscolor = 'peru'
pluscolor = 'blue'
minuscolor = 'red'
diffcolor = 'green'


def dmy(ts):
    return datetime.strptime(ts,'%Y%m%d%H%M%S').strftime('%d.%m.%Y')


def hm(ts):
    return datetime.strptime(ts,'%Y%m%d%H%M%S').strftime('%H:%M')


def timestamp(t=None):
    if not t:
        t = datetime.now()
    return t.strftime('%Y%m%d%H%M%S')


def dtfromstamp(ts):
    return datetime.strptime(ts, '%Y%m%d%H%M%S')


def backup(fn):
    t = timestamp()
    try:
        shutil.copy(fn, 'bkp'+os.sep+fn+'.'+t)
    except FileNotFoundError:
        print('Cannot copy %s to %s' % (fn, 'bkp'+os.sep+fn+'.'+t))


def cuttext(text,length=25):
    if len(text)>length:
        return text[:length-3]+'...'
    else:
        return text


def sweep_backup():
    pass
    # function for sweeping unnecessary backup older than set limit (14 days)
    # must be sure there will always be at least one back up of the file
    # after switching do sqlite this will be most probably useless


class Customer(object):
    def __init__(self,datalist=None):
        (self.usercode, self.name, self.surname, self.street,
         self.city, self.zip, self.email, self.tel, self.note1,
         self.note2, self.purchases) = tuple([None]*11)
        if datalist:
            try:
                [self.usercode, self.name, self.surname, self.street, self.city, self.zip, self.email, self.tel, \
                 self.note1, self.note2]=datalist[:10]
                self.purchases = datalist[10]
            except:
                pass # just leave the default values (None)

    def change(self,keyword, value):
        """

        :type keyword: defines what is going to be changed: 'usercode', 'name', 'surname', 'street', 'city', 'zip',
            'email', 'tel', 'note1', 'note2'
        :type value: a new value attached to keyword
        """
        for (kw, attr) in ('usercode', self.usercode), ('name', self.name), ('surname', self.surname),\
            ('street',self.street), ('city',self.city), ('zip', self.zip), ('email', self.email), ('tel', self.tel), \
            ('note1', self.note1),('note2', self.note2):
            if keyword == kw:
                attr = value

    def add_purchase(self,price):
        if not isinstance(price, Purchase):
            price = Purchase(price)
        self.purchases.append(price)

    def add_discount(self,price):
        if not isinstance(price, Purchase):
            price = Purchase(price, True)

    def output(self):
        return ';'.join(map(str,[self.usercode, self.name, self.surname, self.street, self.city, self.zip, self.email, self.tel, \
                 self.note1, self.note2]))


class Purchase(object):
    def __init__(self, price, discount=False, ts=timestamp() ):
        """
        :type price: float, actual purchase price (before discount applied)
        :type discount: False if discount not applied (fullpriced purchase), True if discount applied
        :type ts: timestamp for Purchase
        """
        self.price = float(price)
        if discount in ['0',0,False, 'False', 'false']: discount = False
        elif discount in ['1',1,True, 'True', 'true']: discount = True
        else: discount = False
        self.discount = discount
        self.ts = ts
        self.ptime = dtfromstamp(ts)

    def __str__(self):
        return '%s %.2f %d' % (self.ts, self.price, self.d() )

    def d(self):
        return 1 if self.discount or self.discount=='1' else 0

    def short(self):
        return '%.2f %d' % (self.price, self.d())

    def __repr__(self):
        return 'Purchase: %s' % self.__str__()

    def finalPrice(self):
        c = 1
        if self.discount: c = 0.9
        return self.price * c

    def gettime(self):
        return ' '.join([dmy(self.ptime),hm(self.ptime)])

    def write(self):
        pass


    # data should be store this way
    #
    # users.ver
    # ---------
    # USERCODE;USERSURNAME;USERNAME;USERSTREET;USERCITY;USERZIP;EMAIL;TEL;USERNOTE1;USERNOTE2 ### ;SUMADD;SUMSUB
    #
    # purchases.ver
    # -----------
    # USERCODE DATE PURCHASE 1
    # USERCODE DATE PURCHASE 1 (FULL PRICE)
    # USERCODE DATE PURCHASE 0 (DISCOUNT)
    # ...
    #
    # log.ver
    # -------
    # TIME event
    #


class GUI(object):

    def __init__(self, master):
        """initialize GUI"""
        #CHOOSE A FILE (XML INPUT)
        self.root = master
        Tk().withdraw()

        self.statustext = StringVar()
        self.status = u''
        self.statustext.set(u'')
       
        # UDAJE ZAKAZNIKA
        self.input_text = StringVar()

        self.label1 = StringVar() # code
        self.label2 = StringVar() # name + surname
        self.label3 = StringVar() # street
        self.label4 = StringVar() # zip + city
        self.label5 = StringVar() # email
        self.label6 = StringVar() # telephone
        self.label7 = StringVar() # note1
        self.label8 = StringVar() # note2
        self.label9 = StringVar() # credit received
        self.label10= StringVar() # credit used
        self.label11= StringVar() # credit diff
        self.label12= StringVar() # claim discount
        self.label20= StringVar()

        self.ldate = [StringVar() for i in range(5)]
        self.lpurchase = [StringVar() for i in range(5)]

        self.activeuser = None

        self.users = {} #self.read_users()
        self.purchases = {} #self.read_purchases()
        self.customers = [] #experimental

        self.last_added = None   # if user is added, this holds his code
                                 # to easily read his data after it is recorded to file

        self.reset_user()
        self.chosen_user = None
        # print self.label12
        self.print_data()
        self.log('GUI initialized')

    def backupfiles(self):
        for f in usersFileName, logFileName, purchaseFileName:
            self.log('Back up files')
            backup(f)

    def get_customer(self):
        return Customer([self.activeuser, self.name, self.surname, self.street, self.city,
                         self.zip, self.email, self.tel, self.note1, self.note2])

    def write_purchase(self,user,purchase,discount=False):
        if not isinstance(purchase, Purchase):
            purchase = Purchase(purchase, discount)
        f = codecs.open(purchaseFileName,'a',encoding='utf-8')
        f.write('%s %s %s\n' % (user, timestamp(), purchase.short()))
        print('%s %s %s\n' % (user, timestamp(), purchase.short()))
        f.close()
        
    def write_all_purchases(self):
        f = codecs.open(purchaseFileName,'w',encoding='utf-8')
        for user in sorted(self.purchases.keys()):
            for epoch in sorted(self.purchases[user].keys()):
                p = self.purchases[user][epoch]
                f.write('%s %s %s\n' % (user, epoch, p.short()))
        f.close()

    # nacitavanie kreditov by sa malo riesit v hlavnom okne pri nacitani zakaznika
    # po pridani alebo ubrani kreditu bz sa mal upatnut slovnik, v ktorom sa budu celu dobu
    # uchovavat hodnoty kredit (transakcie)
    # treba do toho vniest trochu logiky
    # treba otestovat ci bude fungova vnorena trieda
    # citat a pisat bz mala vediet hlavna funkcia, dokonca mozu byt aj globalne 
    def read_purchases(self):
        self.purchases = {}
        credit = []
        if purchaseFileName in os.listdir(os.getcwd()):
            #print 'purch'
            f = codecs.open(purchaseFileName,'r',encoding='utf-8')
            credit = map(lambda x: x.split(),f.readlines())
            f.close()
        else:
            #print 'no purch'
            f = open(purchaseFileName,'w')
            f.close()

        for c in credit:
            d = 0
            if len(c)>=4:
                d = int(c[3])
            self.purchases.setdefault(c[0],{})[c[1]] = Purchase(c[2],d, c[1])
        return self.purchases

    # spocita vsetky kredity 1 uzivatela
    def sum_purchases(self,type = 0):
        """
        :type regular:  if type=0, only regular (fullpriced) purchases are counted
                        if type=1, only discounted purchases are counted
                        if type=2, number of discounts summed
        """
        if self.activeuser and self.activeuser in self.purchases:
            # filter self.purchases[user] [epoch] -> Purchase = {.price, .discount, .timestamp }
            if type==0:
                return sum([x.price if not x.discount else 0 for x in self.purchases[self.activeuser].values()])
            elif type==1:
                return sum([x.price if x.discount else 0 for x in self.purchases[self.activeuser].values()])
            else:
               return sum([1 if x.discount else 0 for x in self.purchases[self.activeuser].values()])
        else:
            #print 'User "%s" not defined or not found in user purchases' % self.activeuser
            #raise ValueError, '[sum_purchases] User "%s" not defined or not found in user purchases' % self.activeuser
            self.update_status('Užívateľ nemá žiadne nákupy.')
            return 0.

    def sum_discounted_purchases(self):
        return self.sum_purchases(1)

    def sum_applied_discounts(self):
        discountValue = 50
        return self.sum_purchases(2)*discountValue

    def plus_minus_purchases(self):
        if self.activeuser and self.activeuser in self.purchases:
            return (self.sum_purchases(), self.sum_purchases(1))
        else:
            #print 'User "%s" not defined or not found in user purchases' % self.activeuser
            #raise ValueError, '[pm_purchases] User "%s" not defined or not found in user purchases' % self.activeuser
            return 0., 0.

 
    def reset_user(self):
        # UDAJE ZAKAZNIKA
        self.usercode = '0'
        self.activeuser = None
        self.name = u'Meno'
        self.surname = u'Priezvisko'
        self.street = u''
        self.city = u''
        self.zip = u''
        self.email = u''
        self.tel = u''
        self.note1 = u''
        self.note2 = u''
        # crplus a crminus budu sluzit neskor na zrychlenie prace
        #zakaznik bude mat definovane posledne hodnoty, aby sme mohli mat
        # nejake breakpointy - napriklad na novy rok sa vsetko vzexportuje
        # a vsetko sa zbiera od zaciatku
        self.crplus = 0  
        self.crminus = 0
        self.crrec = 0.
        self.crused = 0.

        self.statustext.set( u'')

        for i in range(5):
            self.ldate[i].set(u'')
            self.lpurchase[i].set(u'')

        self.update_status(u"Nie je načítaný zákazník.")

        self.users = self.read_users()
        self.purchases = self.read_purchases() 

    def print_data(self):
        self.label1.set(cuttext(self.usercode))
        self.label2.set(cuttext(self.name+' '+self.surname))
        self.label3.set(cuttext(self.street))
        x = ' '
        if not self.zip: x = ''
        self.label4.set(cuttext(self.zip+' '+self.city))
        self.label5.set(cuttext(self.email))
        self.label6.set(cuttext(self.tel))
        self.label7.set(cuttext(self.note1))
        self.label8.set(cuttext(self.note2))

        self.label9.set('+ %7.2f' % self.crrec)
        self.label10.set('- %7.2f' % abs(self.crused))
        diff = self.crrec-abs(self.crused)
        self.label11.set('= %7.2f' % abs(diff))

        self.claimdiscount= ''
        if diff >= limit:
            self.claimdiscount = u'Zákazník má nárok na zľavu.'
        else:
            self.claimdiscount = u'Zákazník ešte musí nakúpiť za %.2f EUR, aby mal nárok na zľavu.' % (limit-diff)

        self.label12.set(self.claimdiscount)

        self.purchases = self.read_purchases() 

        last = []
        uc = self.usercode
        try:
            last = sorted(self.purchases[uc].keys(), reverse = True)[:5]
        except:
            self.update_status(u'Neviem zistiť posledné nákupy pre %s' % self.usercode)

        j = 0
        for date in last:  
            p = self.purchases[uc][date]
            self.ldate[j].set(dmy(date)+'@'+hm(date))
            self.lastplab[j].config(fg=fgcolor1)
            appdisc = ''
            if p.discount:
                self.lastplab[j].config(fg=fgcolor2)
                appdisc = '**'
            self.lpurchase[j].set('%s%.2f%s'% (appdisc, p.price, appdisc))
            j+=1
        if uc!='0':
            self.update_status(u'OK')
        else:
            self.update_status(u'Nie je načítaný vôbec žiaden zákazník.')
        

    def log(self,text='',filename=logFileName):
        
        f = codecs.open(filename,'a',encoding='utf-8')
        f.write(time.strftime('%Y%m%d%H%M%S')+' '+text+'\n')
        f.close()

    def update_status(self,text = ''):
        self.status = text
        #self.statustext.set(text)
        self.statustext.set(text)

    def reset(self):
        "Resets user code and blanks the window."
        pass # 

    def read_users(self, print_status = False):
        userlines = []
        users = {}
        try:
            f = codecs.open(usersFileName,'r',encoding='utf-8')
            userlines = filter(None, f.readlines())
            f.close()
        except:
            self.update_status(u'Neviem načítať užívateľov.')
            return {}

        for line in userlines:
            usl = line.rstrip().split(';')
            users[usl[0]] = usl[:10]

        if print_status:
            self.update_status(u'Načítaných %d užívateľov.' % len(self.users))
        return users

    def write_users(self, print_status = False):
        backup(usersFileName)

        f = codecs.open(usersFileName,'w',encoding='utf-8')
        for user in sorted(self.users.keys()):
             f.write(';'.join(self.users[user])+'\n')
        f.close()

        if print_status:
            self.update_status(u"Užívatelia zapísaní do súboru.")

    def set_user(self,a):
        if a=='-1':
            if self.last_added:
                self.activeuser = self.last_added
            else:
                self.activeuser = None
        if a in self.users.keys():
            self.activeuser = a
        else:
            self.activeuser = None

        au = self.activeuser

        if au:
            [self.usercode, self.name,self.surname, self.street, self.city,self.zip,
             self.email, self.tel, self.note1, self.note2 ] = self.users[au]
                # optional = usl.split(';')[10:]
                # self.xcrrec = 0.
                # self.xcrused = 0.
                # try:
                #     self.xcrrec = float(optional[0])
                # except:
                #     pass
                #     #print 'Neviem nastavit prijate kredity'
                # try:
                #     self.xcrused = float(optional[1])
                # except:
                #     pass
                #     #print 'Neviem nastavit pouzite kredity'

                # NACITAT ZAKAZNIKOVE NAKUPY
            self.purchases = self.read_purchases()
            self.crrec, self.crused = self.sum_purchases(), self.sum_purchases(2)*50 # self.plus_minus_purchases()
            self.status = u''
            self.update_status(u'')
            #self.print_data()
            self.input_text.set(u'')
        else:
            self.update_status(u'Neznámy užívateľ.')
            self.reset_user()
       
        return au

#  pri zadaní -1 by mohol načítať posledného pridaného
    def get_user(self,u=None):
        "Reads user code and finds data in database and fill in."
        self.reset_user()

        if u is None:
            u = self.ib.get()

        self.log('GET USER %s' % u)

        self.set_user(u)

        self.print_data()



    def get_user_name(self):

        def reg(s):
            return s.replace('*', '.*').lower()+'.*'

        def us(k,i):
            return self.users[k][i].lower() 
        
        "Looks for user according to his name and fill in."
        s = self.ib.get().strip()
        self.log('GET USER NAME %s' % s)
        self.users = {}
        self.users = self.read_users()

        l = set()
        for k in filter(None,self.users.keys()):
            if ' ' not in s:
                # HLADAME LEN MENO ALEBO PRIEZVISKO
                if re.match(reg(s),us(k,2)):
                    l.update([k])
                if re.match(reg(s),us(k,1)):
                    l.update([k])
            else:
                # HLADAME MENO A PRIEZVISKO
                m = s.split()
                
                if re.match(' '.join(map(reg,m)), us(k,2)+' '+us(k,1)) or re.match(' '.join(map(reg,m)), us(k,1)+' '+us(k,2)):
                    l.update([k])

        # l obsahuje vsetky keys zodpovedaujuce zadanemu stringu
        # selected je dict, kde su len zodpovedajuci useri z komplet zoznamu
        selected = {k:self.users[k] for k in l}
        
        finduserwindow = Tk()
        finduserwindow.title('BIO-MARKET :: VERNE :: Vyhľadanie zákazníka')
        finduserwindow.geometry('%dx%d' % (460,min([45+len(selected)*30,1000])))
        finduserwindow.configure(bg=bgcolor5)
        g2 = findU(self,finduserwindow)
        g2.main(selected)
        finduserwindow.mainloop()
        #print 'vysledok:', chosen_user
        #global chosen_user

        if self.chosen_user:
            self.get_user(self.chosen_user)
        
        self.chosen_user = None
        #self.print_data()


    def find_name(self):
        "Find a user in a scrollable list of users and choose."
        self.users = {}
        self.log('FIND NAME')
    

    def add_user(self):
        "Adds user to database."
        self.log('ADD USER')

        adduserwindow = Tk()
        adduserwindow.title('BIO-MARKET :: VERNE :: Registrácia zákazníka')
        adduserwindow.geometry('420x280')
        adduserwindow.configure(bg=bgcolor1)
        g1 = editU(self,adduserwindow)
        g1.main_dialog()
        adduserwindow.mainloop()

        if self.chosen_user:
            self.get_user(self.chosen_user)

        self.chosen_user = None
        self.print_data()

    def edit_user(self):
        "Edits existing user in database."
        print(self.usercode)
        if self.usercode and self.usercode in self.users:
            self.log('EDIT USER %s' % self.usercode)

            adduserwindow = Tk()
            adduserwindow.title('BIO-MARKET :: VERNE :: Úprava zákazníka')
            adduserwindow.geometry('420x280')
            adduserwindow.configure(bg=bgcolor3)
            g1 = editU(self, adduserwindow, self.usercode)
            g1.main_dialog()
            adduserwindow.mainloop()

            if self.chosen_user:
                self.get_user(self.chosen_user)

            self.chosen_user = None
            self.print_data()
        else:
            showwarning(
                u"Nie je vybraný žiadny zákazník.",
                u"Nie je vybraný žiadny zákazník, nemôžem editovať." )


### KREDIT STACI PRIDAVAT CEZ ENTRY, NETREBA OTVARAT NOVE OKNO ##########
    def add_purchase(self, regular = True):
        "Adds user to active user."
        cr = self.ib.get()
        c = None

        self.input_text.set(u'')

        try:
            c = float(cr.replace(',', '.'))
        except:
            self.update_status(u'Neviem skonvertovať na číslo')
            self.log('ADD CREDIT %s TO %s UNSUCCESSFUL' % (cr, self.activeuser))
        
        if self.activeuser and c:

            result = self.ask(u'Pridať kredit',u"""Naozaj pridať kredit %.2f\n
zákazníkovi [%s]: %s %s?""" % (c, self.activeuser, self.name, self.surname),
                              u'Kredit %.2f pridaný.' % c,u'Kredit %.2f nebol pridaný.' % c )
            print(result)
            if result:
                self.purchases.setdefault(self.activeuser,{})[timestamp()] = Purchase(c)
                
                self.write_purchase(self.activeuser, Purchase(c))
                self.crrec += c
                self.log('ADD CREDIT %s %.2f' % (self.activeuser, c))
            else:
                self.log('ADD CREDIT %s %.2f CANCELLED' % (self.activeuser, c))
            self.print_data()
                

    def ask(self,info,question,okanswer='', cancelanswer=''):
        result = askokcancel(info, question, icon='warning')
        if result:
            self.update_status(okanswer)
            print(okanswer)
        else:
            self.update_status(cancelanswer)
            print(cancelanswer)
        return result


    def discount(self):
        # najskor treba skontrolovat ci ma zakaznik aspon 50e kredit
        # potom treba zistit, za kolko nakupuje, teda aku ma zlavu
        diff = self.crrec-abs(self.crused)
        if diff<50.:
            showinfo(
            u"Nedostatočný kredit",
            u"Na získanie zľavy potrebuje zákazník kredit aspoň 50 Eur.\nMomentálne má %.2f." % diff )
        else:        
            cr = self.ib.get()
            c = 0.
            try:
                c = float(cr)
            except ValueError:
                # spits the window telling you must enter the price
                showwarning( u"Chýba suma alebo nebolo zadané číslo.",
                             u"Na získanie zľavy treba zadať aj výšku aktuálneho nákupu." )
            else:
                if self.activeuser and c:
                    result = self.ask(u'Aplikovať zľavu',u"""Naozaj aplikovať zľavu na nákup %.2f\n
zákazníkovi [%s]: %s %s?""" % (c, self.activeuser, self.name, self.surname),u'Kredit %.2f pridaný.',u'Kredit %.2f nebol pridaný.' )
                    print(result)
                    if result:
                        self.purchases.setdefault(self.activeuser,{})[timestamp()] = Purchase(c,True)

                        self.write_purchase(self.activeuser, Purchase(c,True))
                        # self.crrec += c
                        self.log('DISCOUNT APPLIED FOR %s TO %.2f' % (self.activeuser,c))
                        self.crused += 50.
                    else:
                         self.update_status('Zľava zrušená.')
                         self.log('ADD CREDIT FOR %s TO %.2f CANCELLED' % (self.activeuser,c))
                else:
                    self.update_status('Zákazník nie je aktívny, alebo nebola nastavená zľava.')
                    self.log('NO ACTIVE USER OR PURCHASE NOT SET FOR DISCOUNT')
        self.print_data()


    def check_backup(self):
        """Backs up a database and log. Uploads through ftp to internet."""
        if 'bkp.lst' in os.listdir(os.curdir):
            if (datetime.now() - dtfromstamp(f.read().split('\n'))).seconds > 1800:
                self.log('AUTO BACK UP')
                self.backupfiles()
                self.update_status('Prebehla záloha súborov.')
                f = open('bkp.lst', 'w')
                f.write(timestamp)
                f.close()
        else:
            self.backupfiles()
            self.update_status('Prebehla záloha súborov.')
            f = open('bkp.lst','w')
            f.write(timestamp)
            f.close()


    def view_log(self):
        "View log."
        pass

    def close(self):
        self.log('GUI closed.')
        self.backupfiles()
        self.root.quit()
        self.root.destroy()

    def main_dialog(self):

        self.basicframe = Frame(self.root)
        self.basicframe.grid()
        self.basicframe.configure(bg=bgcolor)

        self.fr = Frame(self.basicframe)
        self.fr.grid(row = 0, column = 0, sticky='W')
        self.fr.configure(bg=bgcolor)

        # input box
        self.ib = Entry(self.fr, width=50, bd=3, bg=entrycolor, textvariable=self.input_text)
        self.ib.grid(row=1, column=1, columnspan=2)

        # function buttons
        butexit = Button(self.fr, text="Exit", width=20, bg=buttoncolor, command=self.close) #self.exit_root)
        butexit.grid(row=12, column=4)

        butbak = Button(self.fr, text="Backup", width=20, bg=buttoncolor, command=self.backupfiles)
        butbak.grid(row=12,column=3)

        butres= Button(self.fr, text="Edituj zákazníka", width=20, bg=buttoncolor, command=self.edit_user)
        butres.grid(row=12,column=2)

        butadduser= Button(self.fr, text="Pridaj zakazníka", width=20, bg=buttoncolor, command=self.add_user)
        butadduser.grid(row=12,column=1)

        butaddcr= Button(self.fr, text="+ kredit", width=20, bg=buttoncolor, command=self.add_purchase)
        butaddcr.grid(row=1,column=4)

        butsubcr= Button(self.fr, text="Aplikuj zlavu", width=20, bg=buttoncolor, command=self.discount)
        butsubcr.grid(row=2,column=4)       

        butfindcode= Button(self.fr, text=u"Načítaj zákazníka", width=20, bg=buttoncolor, command=self.get_user)
        butfindcode.grid(row=1,column=3)       

        butfindname= Button(self.fr, text=u"Hľadaj meno", width=20, bg=buttoncolor, command=self.get_user_name)
        butfindname.grid(row=2,column=3)

        self.stat = Label(self.fr,text=self.status,bg=labelbgcolor, fg=statuscolor)
        self.stat.grid(row = 2, column = 1, columnspan = 2)

        self.label1.set(cuttext(self.usercode))
        self.lab1 = Label(self.fr,textvariable=self.label1, bg=labelbgcolor, justify='left')
        self.lab1.grid(row = 3, column = 1)

        self.label2.set(cuttext(self.name+' '+self.surname))
        self.lab2 = Label(self.fr,textvariable=self.label2, bg=labelbgcolor, justify = 'left')
        self.lab2.grid(row = 4, column = 1)

        self.label3.set(cuttext(self.street))
        self.lab3 = Label(self.fr,textvariable=self.label3, bg=labelbgcolor, justify = 'left')
        self.lab3.grid(row = 5, column = 1)

        self.label4.set(cuttext(self.zip+' ' if self.zip else ''+self.city))
        self.lab4 = Label(self.fr,textvariable=self.label4, bg=labelbgcolor, justify = 'left')
        self.lab4.grid(row = 6, column = 1)

        self.label5.set(cuttext(self.email))
        self.lab5 = Label(self.fr,textvariable=self.label5, bg=labelbgcolor, justify = 'left')
        self.lab5.grid(row = 7, column = 1)

        self.label6.set(cuttext(self.tel))
        self.lab6 = Label(self.fr,textvariable=self.label6, bg=labelbgcolor, justify = 'left')
        self.lab6.grid(row = 8, column = 1)

        self.label7.set(cuttext(self.note1))
        self.lab7 = Label(self.fr,textvariable=self.label7, bg=labelbgcolor, justify = 'left')
        self.lab7.grid(row = 9, column = 1)

        self.label8.set(cuttext(self.note2))
        self.lab8 = Label(self.fr,textvariable=self.label8, bg=labelbgcolor, justify = 'left')
        self.lab8.grid(row = 10, column = 1)

        self.lab9 = Label(self.fr,textvariable=self.label9, font="Calibri 10 bold", bg=labelbgcolor, fg=pluscolor, justify = 'right')
        self.lab9.grid(row = 4, column = 2)

        self.lab10 = Label(self.fr,textvariable=self.label10, font="Calibri 10 bold", bg=labelbgcolor, fg=minuscolor, justify = 'right')
        self.lab10.grid(row = 5, column = 2)

        self.crdiff = self.crrec - abs(self.crused)
        self.lab11 = Label(self.fr,textvariable=self.label11, font="Calibri 10 bold", bg=labelbgcolor, fg=diffcolor if self.crdiff>=50. else 'black', justify = 'right')
        self.lab11.grid(row = 6, column = 2)

        self.claimdiscount= ''
        if self.crdiff>limit:
            self.claimdiscount = u'Nárok na zľavu.'
        else:
            self.claimdiscount = u'Chýba %.2f EUR na nárok na zľavu.' % (limit-self.crdiff)

        self.label12.set(self.claimdiscount)
        self.lab12 = Label(self.fr,textvariable=self.label12, bg=labelbgcolor, justify = 'left', wraplength=140)
        self.lab12.grid(row=7, column=2, rowspan=3)

        self.label20.set(u'POSLEDNÉ NÁKUPY')
        self.lab20 = Label(self.fr,textvariable=self.label20, bg=labelbgcolor, justify = 'center', wraplength=140)
        self.lab20.grid(row=3, column=3, columnspan=2)

        last = []
        try:
            last = sorted(self.purchases[self.usercode].keys(), reverse = True)[:5]
        except:
            self.update_status(u'Neviem zistiť posledné nákupy pre %s' % self.usercode)

        self.lastdlab = [Label(self.fr,textvariable=self.ldate[r], bg=labelbgcolor, fg=fgcolor1, justify = 'left') for r in range(5)]
        self.lastplab = [Label(self.fr,textvariable=self.lpurchase[r], bg=labelbgcolor, fg=fgcolor1, justify = 'right') for r in range(5)]

        for i in range(5):
            self.ldate[i].set(u'')
            self.lpurchase[i].set(u'')
            self.lastdlab[i].grid(row=4+i, column=3)
            self.lastplab[i].grid(row=4+i, column=4)

        j = 0
        print(last)
        for l in last:
            print('l',l)
            p = self.purchases[self.usercode][l]
            self.ldate[j].set(dmy(l))
            self.lpurchase[j].set(p.price)
            j+=1

    def exit_root(self):
        self.destroy()
        self.quit()
        sys.exit()



class editU(GUI):
    def __init__(self, parent, master, customer = None):
        self.root = master
        Tk().withdraw()

        self.users = parent.read_users()
        self.parent = parent
        self.customer = customer

    def status_update(self,text=''):
        parent = self.parent
        parent.status = text
        parent.statustext.set(parent.status)

    def register(self):
        parent = self.parent
        # READ DATA
        usercode = self.e1.get()
        name = self.e2.get()
        surname = self.e3.get()
        street = self.e4.get()
        city = self.e5.get()
        azip = self.e6.get()
        email = self.e7.get()
        tel = self.e8.get()
        note1 = self.e9.get()
        note2 = self.e10.get()
        crrec = '0.00'
        if not self.customer:
            crrec = self.e11.get().replace(',','.')
            try: float(crrec.replace(',','.'))
            except: crrec = '0.00'

        usercodes = set(self.users.keys())
        if usercode and (name or surname):
            if usercode in usercodes and not self.customer:
                parent.log(u'Pokus pridať existujúceho zákazníka %s.' % usercode)
                parent.update_status(u'Číslo karty už existuje!')
            else:
                self.users[usercode] = [usercode, name, surname, street, city,
                                azip, email, tel, note1, note2]
                parent.users[usercode] = self.users[usercode]
                if not self.customer:
                    self.write_purchase(usercode,crrec)
                    self.last_added = usercode
                #WRITE DATA
                self.write_users()

                self.close()
                parent.chosen_user = usercode
                parent.usercode = usercode
                return usercode
        else:
            self.log(u'Pokus pridať zákazníka bez čísla a/alebo bez mena.')
            self.status_update( u'Je potrebné zadať číslo karty a aspoň meno alebo priezvisko.' )

    def close(self):
        self.root.quit()
        self.root.destroy()        


    def main_dialog(self):
        self.basic = Frame(self.root)
        self.basic.grid()
        self.basic.configure(bg=bgcolor1)

        self.fr = Frame(self.basic)
        self.fr.grid(row = 0, column = 0, sticky='W')
        bkg = bgcolor1
        ec = entrycolor1
        btc = buttoncolor1
        if self.customer:
            bkg = bgcolor3
            ec = entrycolor3
            btc = buttoncolor3
        self.fr.configure(bg=bkg)

        # input box

        l1 = Label(self.fr, text=u"Číslo karty", width = 20, bg=bkg)
        l1.grid(row=1,column = 1)
        l2 = Label(self.fr, text="Meno", width = 20, bg=bkg)
        l2.grid(row=2,column = 1)
        l3 = Label(self.fr, text="Priezvisko", width = 20, bg=bkg)
        l3.grid(row=3,column = 1)
        l4 = Label(self.fr, text="Ulica", width = 20, bg=bkg)
        l4.grid(row=4,column = 1)
        l5 = Label(self.fr, text="Mesto", width = 20, bg=bkg)
        l5.grid(row=5,column = 1)
        l6 = Label(self.fr, text=u"PSČ", width = 20, bg=bkg)
        l6.grid(row=6,column = 1)
        l7 = Label(self.fr, text="Email", width = 20, bg=bkg)
        l7.grid(row=7,column = 1)
        l8 = Label(self.fr, text=u"Telefón", width = 20, bg=bkg)
        l8.grid(row=8,column = 1)
        l9 = Label(self.fr, text=u"Poznámka 1", width = 20, bg=bkg)
        l9.grid(row=9,column = 1)
        l10 = Label(self.fr, text=u"Poznámka 2", width = 20, bg=bkg)
        l10.grid(row=10,column = 1)

        if not self.customer:  # if edit existing customer, first
            l11 = Label(self.fr, text=u"Počiatočný kredit", width = 20, bg=bkg)
            l11.grid(row=11,column = 1)

        l12 = Label(self.fr, textvariable=self.parent.status, bg = bkg, justify='left')
        l12.grid(row=12,column=1, columnspan=2)

        self.e1 = Entry(self.fr, width = 40, bd=3, bg=ec)#, textvariable=self.usercode)
        self.e1.grid(row=1, column=2)
        self.e2 = Entry(self.fr, width = 40, bd=3, bg=ec)#, textvariable=self.name)
        self.e2.grid(row=2, column=2)
        self.e3 = Entry(self.fr, width = 40, bd=3, bg=ec)#, textvariable=self.surname)
        self.e3.grid(row=3, column=2)
        self.e4 = Entry(self.fr, width = 40, bd=3, bg=ec)#, textvariable=self.street)
        self.e4.grid(row=4, column=2)
        self.e5 = Entry(self.fr, width = 40, bd=3, bg=ec)#, textvariable=self.city)
        self.e5.grid(row=5, column=2)
        self.e6 = Entry(self.fr, width = 10, bd=3, bg=ec)#, textvariable=self.azip)
        self.e6.grid(row=6, column=2, sticky='w')
        self.e7 = Entry(self.fr, width = 40, bd=3, bg=ec)#, textvariable=self.email)
        self.e7.grid(row=7, column=2)
        self.e8 = Entry(self.fr, width = 40, bd=3, bg=ec)#, textvariable=self.tel)
        self.e8.grid(row=8, column=2)
        self.e9 = Entry(self.fr, width = 40, bd=3, bg=ec)#, textvariable=self.note1)
        self.e9.grid(row=9, column=2)
        self.e10 = Entry(self.fr, width = 40, bd=3, bg=ec)#, textvariable=self.note2)
        self.e10.grid(row=10, column=2)

        if self.customer:  # if editing existing customer
            p= self.parent
            pairs = tuple(zip([self.e1, self.e2, self.e3, self.e4, self.e5, self.e6, self.e7, self.e8, self.e9, self.e10],
                [p.usercode,p.name,p.surname,p.street,p.city,p.zip,p.email,p.tel,p.note1,p.note2]))
            for en,txt in pairs:
                en.insert('end', txt)
        else:
            self.e11 = Entry(self.fr, width = 10, justify = 'left',  bd=3, bg= ec)#, textvariable=self.cr)
            self.e11.grid(row=11,column = 2, sticky='w')

        # function buttons
        self.butclose = Button(self.fr, text = u"Zrušiť", width=20, justify='center', bd=3, bg=btc, command = self.close) #self.exit_root)
        self.butclose.grid(row=12, column=1)

        self.butreg = Button(self.fr, text = u"Odoslať", width=20, justify='center', bd=3, bg=btc, command=self.register)
        self.butreg.grid(row=12,column=2)        


class findU(GUI):
    def __init__(self, parent, master):
        self.root = master
        Tk().withdraw()
        self.parent = parent

    def close(self):
        self.root.quit()
        self.root.destroy()        

    def choose(self,u=None):
        self.parent.chosen_user = u
        self.close()
        

    def main(self, su):

        def gn(l): # get "surname name" from list of data
            return l[2]+' '+l[1]
        
        self.basic = Frame(self.root)
        self.basic.grid()
        self.basic.configure(bg=bgcolor5)

        self.fr = Frame(self.basic)
        self.fr.grid(row = 0, column = 0, sticky='W')
        self.fr.configure(bg=bgcolor5)

        nadpis = Label(self.fr, text=u"VYBER ZÁKAZNÍKA", width = 20, justify='center', bg=bgcolor5)
        nadpis.grid(row=1,column=1)

        buttons = []

        sortkeys = sorted(su, key = lambda x: ' '.join(su.get(x)[2::-1]))

        for k in sortkeys:   # !!!!!!
            txt = ', '.join([k]+[gn(su[k])]+su[k][3:5])
            buttons.append(Button(self.fr, text = txt, width=65, justify='left', bd=2, bg=buttoncolor4, command = lambda u=k:self.choose(u)))
            buttons[-1].grid(row = len(buttons)+2, column = 1)

        self.butcanc = Button(self.fr, text = u"Zrušiť", width=20, justify='center', bd=2, bg=buttoncolor5, command=self.close)
        self.butcanc.grid(row=len(su)+4,column=1)        


root = Tk()
root.title('BIO-MARKET :: VERNE :: Zákaznícky vernostný systém')
root.geometry('610x248')
root.configure(bg = bgcolor)
g = GUI(root)
g.main_dialog()
root.mainloop()
