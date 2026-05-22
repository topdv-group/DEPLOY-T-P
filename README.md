"# DEPLOY-T-P" 


pip install flask firebase-admin python-dotenv
pip freeze > requirements.txt
Create .env
    .env

    Example contents:
    SECRET_KEY=mysecretkey
    FIREBASE_KEY_PATH=serviceAccountKey.json
   

Create .gitignore
    venv/
    .env
    firebase/serviceAccountKey.json
    __pycache__/

C:\Users\Aldo\OneDrive\Documents\KABAYA\TUMIRA\tap_and_pay>git remote add origin https:

C:\Users\Aldo\OneDrive\Documents\KABAYA\TUMIRA\tap_and_pay>git config --global user.name "topdv-group"

C:\Users\Aldo\OneDrive\Documents\KABAYA\TUMIRA\tap_and_pay>git config --global user.email ""

errors: 1
    I tried to get the -snap_shot = target_ref.order_by_child("phone").get()
    and got the following errors - "error": "Failed to retrieve employee data: Index not defined, add \".indexOn\": \"phone\", for path \"/EMPLOYEES\", to the rules"

    solution: replaced firebase rules with {
        "rules": {
            ".read": false,
            ".write": false,
            "EMPLOYEES": {
            ".indexOn": ["phone"]
            }
        }
        }
    result: it worked fine.

    errors:2
        sometimes the .env variables get collapse and when you post it say {jwt} ERRORS you
        have to go back to firebase console settings and generate new files and replace it with the one
        that you had.

CONNECTING Ngrook so that the local server is connected on the internet in order to use pawapay WEBHOOK
---functionalities

    -https://ngrok.com/#3Dd7ps310lE39XXfeORi669piqF_4dJ6f4n3EdxQRtnPvmB9qss
    -Download the appropriate ngrok agent for your operating system (Windows, macOS, or Linux).
    -In your ngrok dashboard, copy your unique Authtoken 
    -ngrok config add-authtoken <YOUR_AUTHTOKEN>
    -Windows users may need to use ./ngrok.exe instead of ngrok if it is not in their system path
    -Start the Tunnel:Ensure your local web server is already running (e.g., on port 8000).
        Run this command to generate your public URL:bashngrok http 8000(in cmd)
    -ngrok http 8000

    -The terminal will display a "Forwarding" address, such as https://<random-id>.ngrok-free.app.

    {Web Interface                 http://127.0.0.1:4040                                                                     Forwarding                    https://banker-goliath-humped.ngrok-free.dev -> http://localhost:5000 }

git commands that are most frequently used when you have a new project
-git init
-git add .
-git commit -m "Initialcommit"
-git branch -M main
-git remote add origin <PASTE_YOUR_COPIED_GITHUB_URL>
-git push -u origin main
-git remote set-url origin https://github.com/topdv-group/Tap-And-Pay
-git push -u origin main
-git pull origin main --allow-unrelated-histories


{Option A: Overwrite GitHub with your local code (Fastest & Easiest)If you are 100% sure that the code on your local computer is the correct, up-to-date version and you want to completely replace whatever is currently on GitHub, you can force the push.Abort the stuck merge:bashgit merge --abort
Use code with caution.Force push your local code:bashgit push origin main --force
Use code with caution.(Warning: This will permanently delete the conflicting versions of those files on GitHub and replace them with your local files).Option B: Keep local files but safely accept them over GitHubIf you want to resolve the conflict cleanly without using a destructive force-push, you can tell Git to automatically favor your local files during the merge.Run the merge again, telling Git to favor your local version ("ours"):bashgit pull origin main --allow-unrelated-histories -X ours
Use code with caution.Commit the resolved merge:bashgit add .
git commit -m "Resolved conflicts favoring local changes"
Use code with caution.Push to GitHub:bashgit push -u origin main
Use code with caution.Option C: Manually review the differencesIf you think the files on GitHub contain important code from a teammate that you don't want to lose, you must review them.Open your project folder in VS Code.Look at the file explorer sidebar; your conflicting files will be highlighted in red with a C next to them.Click on a file like tapandpay_server.py. You will see visual buttons at the top of the conflict area: "Accept Current Change" (your local code) or "Accept Incoming Change" (GitHub's code).Click the option you prefer for each file, save the files, and run:bashgit add .
git commit -m "Manually resolved conflicts"
git push -u origin main}

Reading
Reading
The error is clear: Gunicorn can't find the Flask app instance. Your run.py has app = create_app(), but Gunicorn is looking for app directly in the app module.

The Problem
Your run.py creates the app, but Gunicorn is trying to import app from the app package (your app/ folder), not from run.py.

Fix: Create a wsgi.py file or modify start command
Option 1: Create wsgi.py in your root directory (RECOMMENDED)
Create a new file called wsgi.py:

python
# wsgi.py - Entry point for Gunicorn
from run import app

# This is what Gunicorn will import
application = app
Then update your render.yaml or Render start command to:

yaml
startCommand: gunicorn wsgi:application

IMPORTANT — Change Start Command in Render Dashboard

Go to:

Render Dashboard

Then:

Open your web service
Go to Settings
Find Start Command
Replace:
gunicorn app:app

WITH:

gunicorn wsgi:application

Save changes.

This is the MOST important fix.

4. Your wsgi.py is Correct

This file is good:

from run import app
application = app

Gunicorn expects:

gunicorn wsgi:application

Meaning:

wsgi.py → variable called application

Which you already did correctly.

5. Your run.py is Also Correct

You already have:

app = create_app()



