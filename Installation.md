## Install and Configure the Application
Download the code to a local directory.    
(One possible method is using ```git clone https://github.com/TeerapatTrepopsakulsin/ku-polls.git```).  
       
Once done, do the following in the directory where you placed the project files. (Initially, ```ku-polls```)



1. Update your Python ```pip``` to the current version.

    ```
    python -m pip install --upgrade pip
    ```

2. Install virtualenv if not already installed

    ```
    python -m pip install virtualenv
    ```

3. Create a virtualenv subdirectory named ```env``` and activate it.


  - Create a virtualenv subdirectory

    ```
    virtualenv env
    ```
  - Activate the virtualenv    
    
    >   Linux and MacOS:
      ```
      source env/bin/activate
      ```

    > MS Windows:
    ```
    env\Scripts\activate
    ```


4. Install required packages inside the virtualenv.

    ```
    python -m pip install -r requirements.txt
    ```

5. In the project root directory, copy ```sample.env``` to ```.env``` (file name begins with "."). Then edit ```.env``` and set values of these variables as desired.     
Some recommendations are already included in the ```sample.env```.   
 
    - This is example ```.env```

        ```
        SECRET_KEY=random-secret-key
        DEBUG=False
        ALLOWED_HOSTS=localhost,127.0.0.1, testserver
        TIME_ZONE=Asia/Bangkok
        ```

6. Run migrations to initialize the database.

    ```
    python manage.py migrate
    ```

7. Import data for some initial polls and users. You can choose the data to download.
    - Download Question and Choice data:
        ```
        python manage.py loaddata data/polls-v4.json
        ```
    - Download Users data:
        ```
        python manage.py loaddata data/users.json
        ```
    - Download Vote data:
        ```
        python manage.py loaddata data/votes-v4.json
        ```
8. Exit the virtualenv.

    ```
    deactivate
    ```

## Run tests
Run unittests in your project files directory:

    
    python manage.py test
    