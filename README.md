## Blackboard marks downloader (UWA)
---
**Dependencies**:
- python
- selenium
- chromedriver, placed relative to this directory

Run the script with `py main.py` and enter your student number and password. I'm not taking your personal details, but *don't take my word for it* - always check the source if you don't trust it!

---

Made this script to download my marks, receipts and all the stuff I uploaded for my first semester. It's a fucking mess of spaghetti python code because to be honest I really just wanted to get this out of the way and have some time for other stuff after the first round of exams. It's a mess of code, with some bits (the login) being picked from the scraper script and some of the scraper asset objects being translated from ruby to python here (in a quick and incomplete way). This will probably will break in some way when the UI is overhauled for next semester :/

There is no bulk marks download feature in the current lms, even though it seems other blackboard installations can give students this bulk download ability. It relies on a lot of js crap so I ended up using selenium all the way through. Doesn't download styles to save space, you'll have to download the css and js yourself and it has to be absolute because the script makes no effort to make the links relative.

This one was made for UWA but you may be able to tweak it for your institution (see constants.py).

Just made it able to download the graded results which may contain annotations. Using a really hacky method to do it so it doesn't create a metadata file for it.

## Note:
* Does not download turnitin reports. You have to click the link manually to the feedback site.
* Does not download multiple submission attempts - only downloads the last/graded attempt.
* Check that the default page is the 'all' category for the marks instead of something else like the submitted category. The script should correct this but just to be safe click on all if it isn't already
* Sometimes chromedriver closes after logging in, when not in headless mode. Try interacting with the page before logging in.