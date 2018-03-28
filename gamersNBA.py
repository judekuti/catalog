from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_setup import *

engine = create_engine('sqlite:///gamersnba.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

# Populate Database for initial kick start
Simon = User(name="Simon Templar", email="simonTemplar@udacity.com",
             picture='/static/img/male.jpeg')
session.add(Simon)
session.commit()

Leanne = User(name="Leanne Smart", email="lsmart@udacity.com",
              picture='/static/img/female.png')
session.add(Leanne)
session.commit()

Jude = User(name="Jude Law", email="jlaw@udacity.com",
            picture='/static/img/male.jpeg')
session.add(Jude)
session.commit()

Mary = User(name="Mary Stuart", email="mm@udacity.com",
            picture='/static/img/female.png')
session.add(Mary)
session.commit()

# Cleveland Cavaliers
cavs = Franchise(name="Cleveland Cavaliers", user_id=1, image="/static/img/cavs.png", conference='East')

session.add(cavs)
session.commit()

lebron = Player(name='Lebron James',
                age=32,
                price='33 million',
                height='6 feet 8 inches',
                weight='280',
                ppg=27,
                position='Small Forward',
                image='/static/img/lebron.png',
                franchise=cavs,
                user_id=1)
session.add(lebron)
session.commit()

TT = Player(name='Tristan Thompson',
                 age=28,
                 price='12 million',
                 height='6 feet 10 inches',
                 weight='290',
                 ppg=10,
                 position='Center',
                 image='/static/img/tt.png',
                 franchise=cavs,
                 user_id=1)
session.add(TT)
session.commit()

hill = Player(name='George Hill',
              age=33,
              price='16 million',
              height='6 feet 5 inches',
              weight='240',
              ppg=15,
              position='Point Guard',
              image='/static/img/hill.png',
              franchise=cavs,
              user_id=1)
session.add(hill)
session.commit()

jordan = Player(name='Jordan Clarkson',
                age=28,
                price='15 million',
                height='6 feet 4 inches',
                weight='180',
                ppg=26,
                position='Shooting Guard',
                image='/static/img/jordan.png',
                franchise=cavs,
                user_id=1)
session.add(jordan)
session.commit()

love = Player(name='Kevin Love',
              age=24,
              price='17.5 million',
              height='6 feet 6 inches',
              weight='230',
              ppg=15,
              position='Power Forward',
              image='/static/img/love.png',
              franchise=cavs,
              user_id=1)
session.add(love)
session.commit()


# Golden State Warriors
gsw = Franchise(name="Golden State Warriors", user_id=2, image="/static/img/gsw.png", conference='West')
session.add(gsw)
session.commit()

steph = Player(name='Steph Curry',
               age=27,
               price='30 million',
               height='6 feet 5 inches',
               weight='200',
               ppg=29,
               position='Shooting Guard',
               image='/static/img/steph.png',
               franchise=gsw,
               user_id=2)
session.add(steph)
session.commit()

KD = Player(name='Kevin Durant',
                 age=29,
                 price='29 million',
                 height='6 feet 10 inches',
                 weight='275',
                 ppg=28,
                 position='Power Forward',
                 image='/static/img/kd.png',
                 franchise=gsw,
                 user_id=2)
session.add(KD)
session.commit()

klay = Player(name='Klay Thompson',
              age=28,
              price='25 million',
              height='6 feet 7 inches',
              weight='235',
              ppg=22,
              position='Point Guard',
              image='/static/img/klay.png',
              franchise=gsw,
              user_id=2)
session.add(klay)
session.commit()

dramond = Player(name='Dramond Green',
                 age=29,
                 price='16 million',
                 height='6 feet 10 inches',
                 weight='285',
                 ppg=13,
                 position='Small Forward',
                 image='/static/img/green.png',
                 franchise=gsw,
                 user_id=2)
session.add(dramond)
session.commit()

young = Player(name='Nick Young',
               age=34,
               price='14 million',
               height='7 feet 0 inches',
               weight='290',
               ppg=6,
               position='Center',
               image='/static/img/young.png',
               franchise=gsw,
               user_id=2)
session.add(young)
session.commit()


# Boston Celtics
celtics = Franchise(name="Boston Celtics", user_id=3, image="/static/img/celtics.png", conference='East')
session.add(celtics)
session.commit()

kyrie = Player(name='Kyrie Irving',
               age=27,
               price='28 million',
               height='6 feet 6 inches',
               weight='190',
               ppg=29,
               position='Shooting Guard',
               image='/static/img/kyrie.png',
               franchise=celtics,
               user_id=3)
session.add(kyrie)
session.commit()

jaylen = Player(name='Jaylen Brown',
                age=21,
                price='19 million',
                height='6 feet 7 inches',
                weight='195',
                ppg=20,
                position='Power Forward',
                image='/static/img/jaylen.png',
                franchise=celtics,
                user_id=3)
session.add(jaylen)
session.commit()

al = Player(name='Al Horford',
            age=28,
            price='22 million',
            height='6 feet 9 inches',
            weight='230',
            ppg=17,
            position='Small Forward',
            image='/static/img/al.png',
            franchise=celtics,
            user_id=3)
session.add(al)
session.commit()

rozier = Player(name='Terry Rozier',
                age=20,
                price='16 million',
                height='6 feet 7 inches',
                weight='210',
                ppg=13,
                position='Point Guard',
                image='/static/img/rozier.png',
                franchise=celtics,
                user_id=3)
session.add(rozier)
session.commit()

baynes = Player(name='Aron Baynes',
                age=30,
                price='14 million',
                height='7 feet 0 inches',
                weight='290',
                ppg=6,
                position='Center',
                image='/static/img/baynes.png',
                franchise=celtics,
                user_id=3)
session.add(baynes)
session.commit()

# Houston Rockets
rockets = Franchise(name="Houston Rockets", user_id=4, image="/static/img/hou.png", conference='West')
session.add(rockets)
session.commit()

harden = Player(name='James Harden',
                age=27,
                price='28 million',
                height='6 feet 6 inches',
                weight='210',
                ppg=32,
                position='Shooting Guard',
                image='/static/img/jamesharden.png',
                franchise=rockets,
                user_id=4)
session.add(harden)
session.commit()

gordon = Player(name='Eric Gordon',
                age=21,
                price='19 million',
                height='6 feet 5 inches',
                weight='205',
                ppg=17,
                position='Power Forward',
                image='/static/img/gordon.png',
                franchise=rockets,
                user_id=4)
session.add(gordon)
session.commit()

ariza = Player(name='Trevor Ariza',
               age=28,
               price='12 million',
               height='6 feet 9 inches',
               weight='240',
               ppg=17,
               position='Small Forward',
               image='/static/img/ariza.png',
               franchise=rockets,
               user_id=4)
session.add(ariza)
session.commit()

paul = Player(name='Chris Paul',
              age=31,
              price='26 million',
              height='6 feet 5 inches',
              weight='210',
              ppg=23,
              position='Point Guard',
              image='/static/img/paul.png',
              franchise=rockets,
              user_id=4)
session.add(paul)
session.commit()

capela = Player(name='Clint Capela',
                age=27,
                price='14 million',
                height='7 feet 0 inches',
                weight='290',
                ppg=6,
                position='Center',
                image='/static/img/capela.png',
                franchise=rockets,
                user_id=4)
session.add(capela)
session.commit()
