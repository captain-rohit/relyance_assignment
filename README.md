This is an application where users can onboard themselves and create account of themselves with initial balance.

Then every user can perform following operations:

1)  Transfer some amount to others using their registered mail id.

2)  Raise a ticket requesting some amount from other users.

3)  Settle the debt amount raised by other users.

4)  Credit his/her own account.

5)  View all transactions made by his/her account.

URL patterns:

1) http://127.0.0.1:5000/user/register [POST] 

2) http://127.0.0.1:5000/user/login [POST]

3) http://127.0.0.1:5000/user/logout [GET]

4) http://127.0.0.1:5000/user/all_transactions [GET]

5) http://127.0.0.1:5000/user/owes [GET]

6) http://127.0.0.1:5000/user/profile [GET]

6) http://127.0.0.1:5000/banking/pay [POST]

7) http://127.0.0.1:5000/banking/ticket [POST]

8) http://127.0.0.1:5000/banking/fulfill [POST]

9) http://127.0.0.1:5000/banking/credit [POST]



Instructions for running it:-

1)  Clone the repository into local machine

2)  Change the directory into 'relyance_assignment'

3)  Install docker and docker-compose in your system according to your desired Operating System.

4)  Make sure the network ports 5000 and 5432 are not engaged.

5)  RUN < docker-compose -f docker-compose.yml up --build > inside terminal.

5)  The application and the Postgresql Databse will start under two separate containers.

6)  Move into the "app_container" in another terminal by running this:
        
        docker ps

        docker exec -it CONTAINER ID /bin/bash

7)  You will be inside /usr/src directory. Now RUN < python >

8)  Inside Python's console RUN < from app import db >
                                < db.drop_all() >
                                < db.create_all() >
                                < db.session.commit() >

9) Exit from the console using Ctrl+D. Now you are all set to make requests.

Instructions for running the APIs:

https://docs.google.com/document/d/1FUrVPNjQWaVHKA9NgMo43DKZrhEwYXE_hcd7j67GX-8/edit?usp=sharing


Thanks