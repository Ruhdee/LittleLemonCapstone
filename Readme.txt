Little Lemon - Back-End Developer Capstone
==========================================

API paths to test
-----------------
/api/users/                    POST    Register a new user (username, email, password)
/api/token/login/              POST    Get an auth token (username, password)
/api/token/logout/             POST    Delete your auth token (needs token)
/api/users/me/                 GET     Show the logged-in user (needs token)

/api/menu-items/               GET     List all menu items (open to everyone)
/api/menu-items/               POST    Add a menu item (staff token only)
/api/menu-items/<id>/          GET     Show one menu item
/api/menu-items/<id>/          PUT, PATCH, DELETE    Change or delete a menu item (staff token only)

/api/bookings/                 GET     List all table bookings (needs token)
/api/bookings/?date=2026-12-01 GET     List bookings for one date (needs token)
/api/bookings/                 POST    Book a table (needs token)
/api/bookings/<id>/            GET, PUT, PATCH, DELETE    View, change or cancel a booking (needs token)

Web pages (static HTML served by Django)
----------------------------------------
/  /about/  /menu/  /menu_item/<id>/  /book/  /reservations/


Setup
-----
1. Create the MySQL database and user (or change USER/PASSWORD in littlelemon/settings.py to your own):
     CREATE DATABASE littlelemon;
     CREATE USER 'admindjango'@'localhost' IDENTIFIED BY 'employee@123!';
     GRANT ALL ON *.* TO 'admindjango'@'localhost';
     FLUSH PRIVILEGES;
2. pipenv install
3. pipenv shell
4. python manage.py migrate
5. python manage.py loaddata menu
6. python manage.py createsuperuser      (a staff user, needed to add or change menu items)
7. python manage.py runserver
8. Run the unit tests: python manage.py test


Testing with Insomnia
---------------------
1. POST http://127.0.0.1:8000/api/users/ with a JSON body:
     {"username": "guest1", "email": "guest1@example.com", "password": "<a strong password>"}
   Expected: 201 Created.
2. POST http://127.0.0.1:8000/api/token/login/ with:
     {"username": "guest1", "password": "<the same password>"}
   Expected: 200 OK and {"auth_token": "..."}.
3. In Insomnia open the Auth tab, choose Bearer Token, paste the token and set the prefix to Token
   (or add the header  Authorization: Token <your token>).
4. POST http://127.0.0.1:8000/api/bookings/ with:
     {"first_name": "Guest", "reservation_date": "2026-12-01", "reservation_slot": 18}
   Expected: 201 Created. Sending the same date and slot again returns 400 because the table is already booked.
   reservation_slot is the hour of the booking, from 10 to 19.
5. GET http://127.0.0.1:8000/api/bookings/ with the token. Without the token you get 401.
6. GET http://127.0.0.1:8000/api/menu-items/ works without a token.
   Adding a menu item needs the token of the superuser from setup step 6:
     POST http://127.0.0.1:8000/api/menu-items/  {"name": "Pasta", "price": 15, "menu_item_description": "Fresh pasta"}
   With a normal user's token the API returns 403.
