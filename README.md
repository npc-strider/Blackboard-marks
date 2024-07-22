## Blackboard marks downloader (UWA)

NOTE: _Who gives a shit about marks? I don't think I am as much of a tryhard as when I first made this script. Either way I'm still patching this when the crappy code breaks at the end of each semester..._

---

**Dependencies**:

- python
- selenium
- chromedriver, placed relative to this directory

Run the script with `py main.py` and enter your student number and password. I'm not taking your personal details, but _don't take my word for it_ - always check the source if you don't trust it!

---

Made this script to download my marks, receipts and all the stuff I uploaded for my first semester.

There is no bulk marks download feature in the current lms, even though it seems other blackboard installations can give students this bulk download ability. Saves visited pages to `URLS.txt` so you can use something like SingleFile extension and use their batch save url feature to save the list of urls visited (I recommend enabling scripts in the singlefile settings so that comments are saved)

This one was made for UWA but you may be able to tweak it for your institution (see constants.py).

Just made it able to download the graded results which may contain annotations. Using a really hacky method to do it so it doesn't create a metadata file for it.

## Note:

- Does not download turnitin reports. You have to click the link manually to the feedback site.
- Does not download multiple submission attempts - only downloads the last/graded attempt.
- Check that the default page is the 'all' category for the marks instead of something else like the submitted category. The script should correct this but just to be safe click on all if it isn't already
- Sometimes chromedriver closes after logging in, when not in headless mode. Try interacting with the page before logging in.
