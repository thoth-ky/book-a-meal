# BOOK A MEAL APP

[![Build Status](https://travis-ci.org/jmutuku95/book-a-meal.svg?branch=tests)](https://travis-ci.org/jmutuku95/book-a-meal)

[![Coverage Status](https://coveralls.io/repos/github/jmutuku95/book-a-meal/badge.svg?branch=master)](https://coveralls.io/github/jmutuku95/book-a-meal?branch=master)

challenge2_features

This is a simple Application to help a restaurant track it's customer's needs and customers make orders easily. The customers
are supposed to create accounts which they can use later to view menus or place orders for meals
The Restaurant staff/caterers use priviledged user accounts which allow them to modify, delete some resources
# Technologies
This application is build using the following technologies

  1. Python 3.6
  2. Flask Microframework
  3. Dependencies specified in _requirements.txt_ file
Ensure you install the above and create a virtual environment with all dependencies. The _.env_ file contains environment variable
you need to set first before running the app
You will need a browser too, to be able to view the webpages, i recommend Firefox v. 59


# UI

The app UI  contains:
  1. User signup and signin pages.
  2. A page where the caterer can manage (i.e: add, modify and delete) meal options in the application.
  3. A page where the caterer can set menu for a specific day by selecting from the meal options available on the system.
  4. A page where the users can see the menu for a specific day and select an option from the menu.
  5.  A page where the caterer can see t he summary of the orders for a specific day and the details for all the orders .

Check it out  at gh-pages using this url https://jmutuku95.github.io/book-a-meal/UI/startpage.html , or just clone this repo into your machine: https://github.com/jmutuku95/book-a-meal.git
# Preview
Home page
![hotcornerhome](https://user-images.githubusercontent.com/28805113/39204996-233f0b4a-4802-11e8-8a1b-9283be8653ec.png)
Menu Page
![menuhotcorner](https://user-images.githubusercontent.com/28805113/39205079-5eef6a68-4802-11e8-917b-6d4f62bab9d3.png)
Order Page
![orderhotcorner](https://user-images.githubusercontent.com/28805113/39205084-63b48ce0-4802-11e8-8dec-9b48c5f7835e.png)

# Testing
To run the tests, **pytest** is recommended, just navigate to project root folder and run py.test in the terminal. The tests
contained here test the following api endpoints:

  1. **_/v1/auth/signup, /v1/auth/signup/_** - For user registration
  2. **_/v1/auth/signin, /v1/auth/signin_** - For user login
  3. **_/v1/meals, /v1/meals/, /v1/meals/\<mealid>/, /v1/meals/\<mealid>_** - For adding, modifying and deleting meals
  4. **_/v1/menu, /v1/menu/_** - For setting up the menu and viewing menu
  5. **_/v1/orders', '/v1/orders/', '/v1/orders/\<orderid>', '/v1/orders/\<orderid>/_** - For editing, adding and viewing menus
  
 The tests also check if user has rights to access the specific endpoint and with what method to ensure integrity is mantained

# Environment
  Ensure your environment contains all libraries specified in _requirements.txt_ 


_Feel free to give suggestions on how to improve the site more._
