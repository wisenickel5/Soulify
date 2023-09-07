# Soulify - Developer Guidance


## Getting Started

In accordance of best practices, the virtual environment will not be committed to 
this project. An exact version of Python is not necessary, just ensure that a 
version >= 3.10.0 is being used. The Python community recommends setting up 
PyEnv to manage different versions of Python on your machine, see here: 
https://realpython.com/intro-to-pyenv/

### _Windows_

Open a PowerShell session "As an Administrator" and run the following command to allow the execution of scripts:
```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine
```

Then run the following command to install PyEnv:
```
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
```

Once PyEnv has been successfully installed, close out of that PowerShell session and open a new session. In the new session, run the following command to ensure PyEnv was installed properly (you should see a PyEnv help menu):
```
pyenv help
```

Next we'll install a version of Python compatible with the Soulify project
```
pyenv install 3.10.0
```

And now set the previously installed version of Python to be used "Globally"
```
pyenv global 3.10.0
```

For peace of mind, we can run the following command to test that the global version of Python was setup properly (There are hundreds of test to be run this may take a while...) Feel free to `Ctrl + C` out of the tests after a bunch have passed.
```
python -m test
```

---

Once the version is set, and the repository has been cloned locally, create a new directory called `venv` and `cd` into it. Then run the following command:

```
python -m venv .
```

This will create a new virtual environment. `cd` out of the venv directory & activate it:

For windows (Powershell Session):

```
.\venv\Scripts\Activate.ps1
```

For Mac & Linux:

```
source venv/bin/activate
```

Once activated, use pip to install the project's dependencies:

```
pip install -r requirements.txt
```

You'll know you have set up the virtual environment properly when you have a folder called
`venv` in the root of the Soulify project.

---

## Running Soulify Locally

In `config.py` you'll notice two REDIRECT_URI variables. The Spotify API uses the REDIRECT URI as a callback URL for the OAuth 2.0 
authorization flow. OAuth 2.0 is commonly used to allow users to log in to applications by authenticating via 
a third-party service like Spotify. The REDIRECT_URI is where the user will be sent after they have authenticated themselves on the Spotify login page.

When running flask locally, `REDIRECT_URI = 'http://127.0.0.1:5000/callback'` should be uncommented to access actual features of the 
Spotify API. Always remember to leave the `REDIRECT_URI = 'https://soulify.herokuapp.com/callback'` line uncommented when
committing to the main branch.

### _In a Mac/Linux Terminal_

Ensure that the venv (virtual environment) has been activated.

Each time a new terminal session is started, the following commands must be run to serve the Flask App on debug mode. 
- `$ export FLASK_APP=run.py`

- `$ export FLASK_ENV=development`

- `$ flask run`


### _In a PowerShell Session_

- `$env:FLASK_APP = "run.py"`

- `$env:FLASK_ENV = "development"`

- `flask run`

**Then open up a web browser of your choice and navigate to http://127.0.0.1:5000/**

---