# Project repository for CS_3240 Group B-08

__Names:__ Brendan Grimes, Megan Maleno, Courtney Nguyen, Kevin Chen, Oliver Mu

__Computing IDs:__ ken6sx, mm6tun, cn9hws, kyc4mr, lm2ceh

When you start working on something, after creating a git branch if you don't have one already, it may be a good idea
to run
```BASH
git checkout main
git pull
git checkout <your-branch-name>
git status                  # just to make sure this shows your branch checked out
git merge main
```
this will update your branch with whatever everyone else has finished working on and merged into the upstream (meaning online, not local) main. If you get a message saying there are merge conflicts, that means that something you are working on conflicts with what is in main. You can resolve them however you like on your branch, but before your branch can be merged back into main you will have to make sure that you didn't break anything that currently works.


Unless you have a good reason not to do so, we should all be using a [python virtual environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/) because it allows us to keep the packages and versions of things we are using uniform across the team

To start the virtual environment (once you have created it according to the instructions linked above):
```BASH
source env/bin/activate      # for Mac/linux users

.\env\Scripts\activate       # for Windows users
```

Once you are in the virtual environment (you should see a little `(env)` or `.venv` or something like that at the left side of your command line prompt), and assuming your git branch is up to date with main, you can run

`pip install -r requirements.txt`

to install any dependencies the team is using. You will likely see an error about `psycopg` or something like that. This can be ignored, as it is an internal heroku thing that we won't need when running locally. Also, if you add any dependencies (e.g., you do a `pip install <something or another>`), you should add the `<something or another>` to the `requirements.txt` file with a comment explaining what its purpose is.

This should also install pylint with the same linting rules everyone else is using, all that should remain to get that to work is to make sure your IDE is using the virtual environment for its python interpreter. (on VSCode you can simply click the version number button right next to the "Python" button at the bottom right to select which interpreter you want, and then choose the one that has a reference to `.venv/env` or something like that).

To start the server locally:
``` BASH
python3 manage.py runserver  # for Mac/linux users

py manage.py runserver       # for Windows users
```

