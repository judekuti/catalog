# Catalog
This is a replica of the Gamers_NBA App but just a prototype to be used to clone a cleaner version of the app for running on the Amazon Lightsail Server configuration 

 

---

### Project Summary
This project employs the Flask framework to develop a RESTful web application. SQLAlchemy a severless database is the persistent storage for data populated.
Authentication was guaranteed using OAuth2 to provide further CRUD functionality on the application. Facebook and Google Accounts authentication were used.


---

## Quick start
#### Requirements
- Python
- Virtual Box
- Vagrant
- FSND virtual machine

## Get Google Client ID
- Visit[https://console.developers.google.com/Google](https://console.developers.google.com/Google)
- Sign up or Login if prompted
- Go to Credentials
- Select Create Crendentials > OAuth Client ID
- Select Web application
- Enter name 'Item-Catalog'
- Authorized JavaScript origins = 'http://localhost:5000'
- Authorized redirect URIs = 'http://localhost:5000/login' && 'http://localhost:5000/gconnect'
- Select Create
- Copy the Client ID and paste it into the data-clientid in login.html
- On the Dev Console Select Download JSON
- Rename JSON file to client_secrets.json
- Place JSON file in this item-catalog directory
- Run application using python app.py

#### Environment Set-Up
- Installation set-up require Unix-Style Terminal or Git Bash Terminal for windows
- Download VirtualBox [virtualbox.org](here)
- Install Vagrant [vagrantup.com](here)
    > Note to make a firewall exception or allow permissions for these downloads
- Check for successful download with `vagrant --version`
- Navigate into the 'vagrant' directory, run ```vagrant up```.
- SSH to the virtual machine with ```vagrant ssh```.

#### Run the program
1. Launch the VM:
    a. `vagrant up`
    b. `vagrant ssh`
2. Within the VM, navigate to `cd /vagrant`
3. Execute the database orm first with `python db_setup.py`
4. Populate the database with an initial set of data with `python gamersnba.py`
5. Execute the program with `python app.py`

---


## JSON Endpoints
 The following are open to the public:

franchise JSON: `/franchise/JSON`
    - Displays all franchises.

franchise/roster JSON: `'/franchise/<int:franchise_id>/roster/JSON'`
   - Displays the roster of a specific franchise

 Category Items JSON: `/franchise/<int:franchise_id>/roster/<int:player_id>/JSON`
   -Displays the profile of a specific player belonging to a specific franchise


## References
- [https://www.python-course.eu](https://www.python-course.eu/index.php)
- [http://www.sqlalchemy.org/](http://www.sqlalchemy.org/)
- [https://www.python-course.eu/index.php](https://www.python-course.eu/index.php)
- [http://flask.pocoo.org/](http://flask.pocoo.org/)


