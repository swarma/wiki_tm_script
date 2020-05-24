# wiki_tm_script
A script based on pywikibot, used for translate and move wikipedia entry to your own wiki.


## Usage

Get pywikibot and script, then moved script in pywikibot

```
cd ~
git clone https://github.com/wikimedia/pywikibot.git
git clone https://github.com/swarma/wiki_tm_script.git
cp wiki_tm_script/source/wiki_text_cleaner.py pywikibot/pywikibot/wiki_text_cleaner.py
cp wiki_tm_script/source/transfer_translate_bot.py pywikibot/scripts
```

Config pywikibot

```bash
# config wiki site address 
python pwb.py generate_family_file.py
# Follow the prompts to enter the robot account information
python pwb.py generate_user_files.py
```

Running Example (when you config target wiki site as swarma):

```bash
touch items.txt
touch zh_items.txt
python pwb.py transfer_translate_bot -family:wikipedia -lang:en -tofamily:swarma -tolang:zh-cn -file:items.txt
```

The number of rows of items.txt and zh_items.txt should be the same, each line is entry name of different language.

## Note

When your wiki is old version, there will be some problems, then using the patch file
```
cp -f source/__init__.py pywikibot/pywikibot/site
wiki_tm_script/source/__init__.py pywikibot/pywikibot/
```

## Todolist
* [ ] Better zh_items.txt
* [ ] Add test
* [ ] Tackle more wiki Grammar problems
