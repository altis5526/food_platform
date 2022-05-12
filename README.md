# Food_platform
This is a repository for the datbase assignment. Feel free to edit this file to list our progress.
## Git commands

I've worked this on Ubuntu and encountered execution errors when using Anaconda on Windows. So...you may still give a try on Windows.
```
## For first time downloading
cd <to your "xampp/htdocs/myapp">
* git clone https://github.com/altis5526/food_platform.git

## For pushing
* git add (--all or specify the file you want to add)
* git commit -m <What did you change>
* git push origin main

## Update local repository (If faced with files updating conflicts, warning messages will pop up and you should choose the final uploading version)
* git pull origin main

## Fetch all files from remote (**Notice: This would overwrite all files in your local dir. Make sure you really need this function!**)
* git fetch --all
* git reset --hard origin/main

## Create branches
* git branch <branch name>
```
You may need to set up your github token when pushing your updated files.

--> `Settings` (Should be in the drop down menu on your right upper screen)

--> `Developer Settings` --> `Personal access tokens`

--> `Generate new tokens` (Select scopes that sound reasonable. I never remember what I've selected) 

--> Done and copy the token when you execute **git push** on your terminal. (Remember to jot down your token as it won't show again once you leave the webpage.)

## Usage
1. Activate xampp.
2. Execute python code.
3. Type in "http://localhost:5000/login" on your browser. (default port is 5000)

## Database dir so far
![image](https://user-images.githubusercontent.com/40194798/167246089-099a6c61-18a1-4fb7-8ba2-9af97035f39e.png)

- the scheme


![image](https://user-images.githubusercontent.com/35695972/167262406-0700f941-f43e-4303-a126-a3848d40a1ee.png)


Attributes in "login" relation
* account_id
* password

You may add some default accounts to test the login system as the sign-up page has not yet completed.
