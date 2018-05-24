# BOOK A MEAL API
[![Build Status](https://travis-ci.org/jmutuku95/book-a-meal.svg?branch=feature-db)](https://travis-ci.org/jmutuku95/book-a-meal) [![Coverage Status](https://coveralls.io/repos/github/jmutuku95/book-a-meal/badge.svg?branch=challenge3)](https://coveralls.io/github/jmutuku95/book-a-meal?branch=challenge3)

This is a simple API to help a restaurant track it's customer's orderss and allow customers make orders easily as well as allow caterers add their meals to menus.
The customers are supposed to create accounts which they can use later to view menus or place orders for meals. The Restaurant staff/caterers use priviledged user
accounts which allow them to modify, delete some resources. The restaurant should at least have one super user created who will promote users to admin status.

# Getting Started
Ensure you have a running python 3.6 virtual environment. See <a href="https://docs.python.org/3/library/venv.html"> this</a> for instructions on how to set up a virtual envronment.
Follow these instructions to setup Book A Meal API

 1. Clone this repositor to your computer
    ```
    $ git clone https://github.com/jmutuku95/book-a-meal.git
    ```

 2. cd to the newly created 'book-a-meal' folder
    ```
    $ cd book-a-meal
    ```

 3. Install all the requiremnets
    ```
    $ pip install -r requirements.txt
    ```

 3. Set the following environment variable
    ```
    $ export SECRET='a random string to be used as your secret key'
    $ export FLASK_APP=book_a_meal.py
    $ export DB_NAME=name_of_database
    $ export DB_PASSWORD=password_to_access_databases
    $ export DB_USER=name_of_user_to_access_database
    $ export APP_SETTINGS=configuration(development, testing or production)
    $ export ORDER_EDITS_UPTO=600
    $ export MAIL_SERVER=preferred_email_server
    $ export MAIL_PORT=email_port
    $ export MAIL_USE_TLS=1
    $ export MAIL_USERNAME=username_for_mail_server
    $ export MAIL_PASSWORD=password_for_mail_server
    ```
  
  4. Make database migrations: While at project root folder, run the following commands.
    ```
    $ python manage.py db init
    ```
    ```
    $ python manage.py db migrate
    ```
    ```
    $ python manage.py db upgrade
    ```

  5. Create super user, while at project root folder
    ```
    python manage.py db create_super_user
    ```

  6. Run tests to ensure everything os ok:
    ```
    $ pytest
    ```

  7. Enter the following command in your terminal
    ```
    $ flask run
    ```

# Prerequisites

This application is build using the following technologies

  1. <a href="https://www.python.org/downloads/">Python 3.6</a>
  2. Flask Microframework
  3. Dependencies specified in _requirements.txt_ file
  4. The API has been hosted at  [Book A Meal API](https://bamv2.herokuapp.com)

Ensure you install the above and create a virtual environment with all dependencies. (Refer Getting Started on how to do this.)

You will need a browser too, to be able to view the webpages, I recommend Firefox v. 60

# UI

The app UI  contains:

  1. User signup and signin pages.
  2. A page where the caterer can manage (i.e: add, modify and delete) meal options in the application.
  3. A page where the caterer can set menu for a specific day by selecting from the meal options available on the system.
  4. A page where the users can see the menu for a specific day and select an option from the menu.
  5. A page where the caterer can see the summary of the orders for a specific day and the details for all the orders .

Check out the UI at gh-pages at Book A Meal UI: [Book A Meal](https://jmutuku95.github.io/book-a-meal/UI/startpage.html)

# PREVIEW
  # Home page
Here is a preview of home page
![hotcornerhome](https://user-images.githubusercontent.com/28805113/39204996-233f0b4a-4802-11e8-8a1b-9283be8653ec.png)

# Testing
The tests were run on postman and the unittests were run using  **pytest**

Below is a screenshot of postman test

 Tests were run on postman, here is an example of the output

  # New User Registration
![user_reg](https://user-images.githubusercontent.com/28805113/39317984-8e728296-4985-11e8-89c7-ca5bb36b6c04.jpg)
 

**STEPS**
 1. Navigate to project root folder **book-a-meal**
 2. Run on your terminal, to see all tests pass and see the coverage
   ```
   $ pytest
   ```

# API endpoints
NB: All endpoints should be prefixed with **_/api/v1_**
For more detailed explanations, see the at [BOOK A MEAL DOCS](https://bookameal0.docs.apiary.io/#)


| EndPoint            | Function                    |METHOD       |
| :-----------------  |-----------------------------|:-----------:|
| /auth/signup        | Sign up new users           | POST        |
| /auth/signin        | Sign In users with accounts | POST        |
| /users              | Get list of all users       | GET         |
| /users/promote/<id> | Make user admin             | PUT         |
| /users/<id>         | Get/delete specific user    | GET, DELETE |
| /meals              | Add a new meal              | POST        |
| /meals              | Get all meals               | GET         |
| /meals/<meal_id>    | Edit/Delete a meal          | PUT, DELETE |
| /menu               | Add/Get menu                | GET, POST   |
| /orders             | Add order, view order       | GET, POST   |
| /orders/<order_id>  | Edit/View specific menu     | GET/ POST   |


  
 The tests also check if user has rights to access the specific endpoint and with what method to ensure integrity is mantained
 
# Authors
* **Joseph Mutuku Kyalo** 

# Acknowledgements
Thanks to the following for reviewing the code:
  * **James Kinyua**
  * **Clement Wekesa**
  * **Sagini Abenga**
  * Everyone I consulted, Peers at Andela Kenya, Online bloggers and the entire Python and Flask community

_Feel free to give suggestions on how to improve the API more._
