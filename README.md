# Incendy

Welcome! This is the repository for the Stardust Labs discord server bot. Incendy was created back in late 2020, simply as a joke to react to certain messages with a certain emoji. Today, Incendy has expanded to become my (catter1) biggest project to date.

## Note

This bot is not meant to be used on other servers. A lot of stuff *will* break! I custom coded Incendy with only the Stardust Labs server in mind. I have been considering making a generalized bot so others can invite it, but for now, Incendy stands by herself.

# Features

## Cogs

- **Admin**: Used to be the cog for updating datapack to Github/Seedfix, but now just has some non-moderation admin functions.
- **Basic**: Where all the miscellaneous "basic" functions are thrown in.
- **Bulletin**: Stores all the commands for posting the embeds in their channels, such as the `#downloads` library.
- **Events**: Handles Discord events and competitions.
- **Faq**: Where the faq and quickpost commands and data live.
- **Helps**: For both the help command, and managing `#support` threads.
- **Moderation**: All the auto moderation tools, as well as fancy manual commands.
- **Remind**: The cog just solely the `/remind` command.
- **Roles**: An offshoot of Moderation, it deals with the auto-assigning of roles.
- **Stats**: The server/member stats command, as well as the Incendy information command.
- **Updater**: A cog handling the automatic updating of all of our projects.
- **Wiki**: Deals with all wiki-related commands and integrations.

## Libraries

- **image_tools**: Various scripts for image editing and color hacks.
- **incendy**: Holds the custom `IncendyBot` class, as well as all the checks and cooldowns.
- **project**: A massive class giving all the functionality to `/upload`.
- **stardust_downloads**: For updating the `downloads` table in the database.

## Resources

- **featured.json**: The list of projects for the `#featured` channel.
- **keys.json**: Where the keys are stored.
- **naughty.txt**: Users will be banned if they say any of the words in this file.
- **pinglog.txt**: For tracking excessive amount of Starmute pings.
- **platforms.json**: Stores data for the `updater` cog and `project` library.
- **settings.json**: Some basic settings and variables for general purpose.
- **textlinks.json**: The "core" textlinks, some of which are auto-updated in the `bulletin` cog.
- **timeout.json**: Tracks users that have been told to "shut up".

# Running Incendy

1. Incendy runs on **Python 3.10**. Older versions will not work, and newer versions are untested.

2. Create a virtual environment.
```bash
# If you do not already have venv installed for 3.10
sudo apt install python3.10-venv

# Navigate to the Incendy bot directory, then initialize and activate the venv
python3 -m venv venv
source venv/bin/activate
```

3. Install the required dependencies.
```bash
pip install -r requirements.txt
```

4. Incendy has some hidden files, which can be viewed in the `.gitignore`. In order to generate a template of those files, run Incendy once. It will fail, but the files will be generated.
```bash
python3 app.py
```

5. Set up PostgreSQL. You should create a user named `incendy`, and insert the password into the `keys.json` file.

6. Fill out the `keys.json` generated inside the `resources` folder.

7. Set your environment variables. These may be set to their default values in step 4, but it is best to set them yourself. Incendy uses three:
- `INCENDY_BOT_TOKEN`: this is *NOT* the bot token, but rather a reference to which token to use from the `keys.json`. Should be set to either `incendy-token` or `dummy-token`. `dummy-token` is used for development purposes.
- `INCENDY_WIKI_UPDATE_ENABLED`: a boolean on whether to auto-update the `wiki` table in the database.
- `INCENDY_STATS_UPDATE_ENABLED`: a boolean on whether to auto-update the `downloads` table in the database.

8. Run Incendy again, and enjoy. The log file is `logs/incendy.log`. Once successfully up and running, Incendy will say:
> Incendy has woken up, ready for an amazing day! Say good morning!

# License and Contributing

Incendy is listed under the [**Stardust Labs License**](https://github.com/Stardust-Labs-MC/license/blob/main/license.txt). What does this mean for a bot?

- You may edit Incendy and use it for your own personal use, but you may not redistribute your modified copy.
- You are forbidden from reuploading Incendy as your own
- Incendy is not fully open source. You may view and edit as much as you want, but for now, I (catter1) will not be accepting contributions from others on the main project.
- You may not use Incendy's image or code for any AI purpose without my (catter1) permission.