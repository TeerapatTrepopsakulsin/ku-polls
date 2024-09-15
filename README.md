# KU Polls: Online Survey Questions 
[![unittest-results](https://github.com/TeerapatTrepopsakulsin/ku-polls/actions/workflows/unittest.yml/badge.svg)](https://github.com/TeerapatTrepopsakulsin/ku-polls/actions/workflows/unittest.yml)

An application to conduct online polls and surveys written in Python and based
on the [Django Tutorial project](https://docs.djangoproject.com/en/5.1/intro/) that lets everyone see the results of a poll question, but only authenticated users can submit or change their own vote, with a limit of one vote per user for every poll. Furthermore, each poll question has its own voting period, during which users can submit or change their votes for the poll, but the poll will always be visible after it has been published even after it voting period has passed.

This app was created as part of the [Individual Software Process](
https://cpske.github.io/ISP) course at [Kasetsart University](https://www.ku.ac.th).

## Installation

See Installation instruction in [Installation.md](Installation.md) or in the [project wiki](../../wiki/Installation).

## Running the Application

1. Start the server in the virtualenv.
   - Activate virtualenv
        > Linux and MacOS:
        ```
        source env/bin/activate
        ```

        > MS Windows:
        ```
        env\Scripts\activate
        ```
   - run the django server
       ```
       python manage.py runserver
       ```

2. You should see this message printed in the terminal window:
   ```
   Starting development server at http://127.0.0.1:8000/
   Quit the server with CTRL-BREAK.
   ```

3. In a web browser, navigate to <http://localhost:8000>. The KU Polls app should be displayed.

4. To stop the server, press CTRL-C in the terminal window. 
   Then exit the virtualenv by closing the window or typing:
   ```
   deactivate
   ```

More detail about [how to run the app](../../wiki/Running-the-Application) in the project wiki.

## Demo User Accounts

Here are 4 demo accounts:

* `demo1` password `hackme11`
* `demo2` password `hackme22`
* `demo3` password `hackme33`
* `demo4` password `hackme44`

You can create more user accounts by sign up in the app.

## Project Documents

All project documents are in the [Project Wiki](../../wiki/Home).

- [Vision and Scope](../../wiki/Vision-and-Scope)
- [Requirements](../../wiki/Requirements)
- [Project Plan](../../wiki/Project%20Plan)
- [Domain Class Diagram](../../wiki/Domain%20Class%20Diagram)
- [Installation](../../wiki/Installation)
- [Running the Application](../../wiki/Running-the-Application)

### Iteration plan
- [Iteration 1 Plan](../../wiki/Iteration-1-Plan)
- [Iteration 2 Plan](../../wiki/Iteration-2-Plan)
- [Iteration 3 Plan](../../wiki/Iteration-3-Plan)
- [Iteration 4 Plan](../../wiki/Iteration-4-Plan)
