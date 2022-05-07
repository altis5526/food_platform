# food_platform
This is a repository for the datbase assignment.
## Git commands

I've worked this on Ubuntu and encountered execution errors when using Anaconda on Windows. So...you may still give a try on Windows.
```
## For first time downloading
cd <to your "xampp/htdocs/myapp">
* git clone <repository>
* (git remote add origin https://github.com/altis5526/food_platform.git) **You may not need this line?**

## For pushing
* git add (--all or specify the file you want to add)
* git commit -m <What did you change>
* git push origin main

## Update local repository
* git pull origin main

## Create branches
* git branch <branch name>
```
You may need to set up your github token when pushing your updated files.

--> `Settings` (Should be in the drop down menu on your right upper screen)

--> `Developer Settings` --> `Personal access tokens`

--> `Generate new tokens` (Select scopes that sounds reasonable, I never remember what I've selected) 

--> Done and copy the token when you execute **git push** on your terminal. (Remember to jot down your token as it won't show again once you leave the webpage.)

## Database dir so far
![image](https://user-images.githubusercontent.com/40194798/167246089-099a6c61-18a1-4fb7-8ba2-9af97035f39e.png)

Attributes in "login" relation
* account_id
* password

You may add some default accounts to test the login system as the sign-up page has not yet completed.
