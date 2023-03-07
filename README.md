# simple-chat
Simple gradio interface for the ChatGPT API
## Current Features
* Runs locally
* Saves conversations to your local computer
* Can load and continue old conversations
* Won't force you to re-login or error out until you refresh
* Cheaper than Plus ($0.0002/1k tokens vs $20/month)
* [Much higher usage limits](https://platform.openai.com/docs/guides/rate-limits)
* [OpenAI won't use data submitted over the API for training and will only retain the data for 30 days](https://platform.openai.com/docs/guides/chat/faq)

![Alt text](/screenshots/ui.PNG?raw=true)

## Installation
### Installing Python:

Go to https://www.python.org/ to download and install the latest version of Python for your operating system.

Follow the instructions to download and run the installer.

Open the Windows Command Prompt by pressing the "Windows" key and typing "Command Prompt".  Once the command prompt is open type "python" to check if Python is installed properly.

![Alt text](/screenshots/python.png?raw=true)

### Installing Libraries:

In command prompt type "pip install gradio==3.16.2" and hit enter.

![Alt text](/screenshots/gradio.PNG?raw=true)

Make sure to run the rest of the commands as well:

```
pip install gradio==3.16.2
pip install openai
pip install markdown
pip install python-dotenv
```

### Generate OpenAI API Key

Go to https://platform.openai.com/account/api-keys and click "Create new secret key" and record the key for later

### Installing and running

To get the file, right click on [this link](https://github.com/borge12/simple-chat/raw/main/simple-chat.py) and select "Save As".  

In Windows Explorer navigate to where simple-chat.py is saved.


Click in the address bar type "cmd" then enter.

![Alt text](/screenshots/cmd.PNG?raw=true)

Command prompt will open, type in "simple-chat.py" and click enter.

![Alt text](/screenshots/simple-chat.PNG?raw=true)

After a moment the simple-chat user interface will launch in your web browser.

Copy and paste your OpenAPI key into the prompt at the top of the page.

![Alt text](/screenshots/addkey.PNG?raw=true)


### Quit or restart web page

To quit the application, you can hit ctrl+c in command prompt to kill the thread.  Sometimes it will need to be run multiple times.  You can hit the up key to cycle through your recent commands in order to quickly relaunch Simple Chat.  

Alternatively, you can just close command prompt to kill the web server.

## Troubleshooting
* If you ran into any issues check command prompt for the errors and post them.  I'll try to help you figure out the issues.
* If you have any of the libraries already installed, I suggest uninstalling and re-installing them.  Specifically, this app works best with an older version of Gradio and I recently updated my instructions above to use that older version.
** Running this will install the correct version over any existing versions.

```
pip install --force-reinstall gradio==3.16.2
```

* If for some reason you need to change your Open API key you can either delete the .env file (which will prompt you to enter on the next launch of the app) or you can edit the file directly in your text editor of choice.

## Known issues
* Max token length is not being handled, so 4000+ tokens will result in no response
* No robust error handling
* Markdown doesn't always work correctly and new lines are not being added correctly
* I haven't done full time development in 10 years...

# Donate
[![Buy me a coffee](https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png)](https://www.buymeacoffee.com/borge12)
