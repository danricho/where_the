# Change Log for WHERE THE ?!?

Last updated: 2023-07-16

**2023-07-16**

 - LATEST!: *Formatted code using Black Formatter and tweaked the javascript for QR scans within the website (workaround for domain change).*

**2023-05-28**

 - 3f23f85: *Sealed flag is now a label (easier to see).*
 - 59e47c7: *Added strip() for stored items on save_json calls.*
 - dfbdcf0: *Add optional 'sealed' and 'destination' attributes to locations*
 - 431ce81: *Hopefully fix the ongoing git issues and show new version availability.*

**2023-05-21**

 - 0227e1e: *Remote repo stops it working... work in progress for the version check stuff.*
 - eac7889: *Minor editing improvement to avoid missing half added items on location save*
 - f9319ac: *Add QR print improvements (and remove single QR print from view page) - Issue #25*
 - 14ee392: *Commit other half of the addition of Location CSV export*
 - 8254ea5: *Add forgotten GitPython dependancy to requirements.txt*
 - d9f1b8a: *Issue #23: Added to readme how to fix ownership ambiguity issue*

**2022-11-24**

 - 80b63de: *Remove additional quote from README.md (#22)*
 - 3fcda2f: *Update README to cover pre-build docker image.*
 - 14d9ad5: *Tweak GitHub Action versions to fix minor metadata config issue.*
 - 238d0a3: *Create GitHub Action to publish Docker Image to GitHub Packages (#21)*

**2022-11-21**

 - e18f520: *Change pill to Spectre CSS from Chota CSS*
 - 48d9029: *Update screenshots for UI update.*
 - 2e84965: *Improved the layout of the entire app; Moved from chota.css to spectre.css; Menu in off-canvas panel; primary color improvements*

**2022-11-15**

 - a6e0e83: *Add detail into Readme regarding docker image rebuild when updating and docker networking*

**2022-11-12**

 - effad56: *Hide footer on print page*

**2022-11-11**

 - fd419b9: *Base Template, Homepage and CSS tweaks*
 - 4e37af9: *Enable Logout button on home when using Authelia (provide Authelia URL in config).*

**2022-11-10**

 - 50866b6: *Add stored location/items count stats to home page*
 - cfad234: *Add configuration option to use colored background for text in label templates*

**2022-11-09**

 - fb95fa8: *Adjust the color of id and description on labels for better readability*
 - ffcee05: *Correct paths for site.webmanifest and browserconfig.xml*

**2022-11-07**

 - ab1d1bd: *Bug fix for login with Authelia*

**2022-11-04**

 - 67c99df: *Homepage spacing adjustment*

**2022-11-03**

 - ac14116: *Updated authentication options to include NO_AUTH, FLASK-LOGIN and AUTHELIA and fix bug for NO_AUTH settings.*
 - 8b4c81e: *Added list pagination, cleaned up some CSS ahead of dark mode*

**2022-10-31**

 - deb0382: *Embed logo SVG on home page to allow it to be color styled by config.yml*
 - 963b793: *Add warning about testing template printing before use.*
 - d2160d2: *Bug fix when scanning QR outside website, there is likely no referrer.*
 - 9dcd256: *Add Github pill back to the footer*

**2022-10-29**

 - bde1f2a: *Add batch printing of labels and templating*
 - 3a61888: *Add update instructions to readme.md*
 - 4b7506e: *Fix edit page bug (lose items on save).*

**2022-10-26**

 - 9d48bd4: *Add dedicated screenshot readme and updated screenshots*
 - 93ce32e: *Smart "Back" buttons for location view page... allows return to search page when came from there.*
 - 8f4d74c: *Add configuration option for including location description under QR code.*
 - 1cdd701: *Print traceback for unhandled exceptions on error page.*

**2022-10-25**

 - aeb2b99: *Add changelog.md*
 - 412c45a: *Turned homepage into menu and moved content to subpages.*
 - 0a03db3: *Fix the Edit page and minor CSS tweak (mistakes earlier)*
 - a2b3284: *Added config option to disable to QR code centre logo*
 - 3b8e00c: *Add primary color configuration option*
 - 419ffbe: *General HTML layout and CSS cleanup*

**2022-10-24**

 - f106572: *Add docker build and compose files*
 - b540e3d: *Minor layout fixes and Readme update*
 - 263d597: *Added rolling buffer for data file backups.*
 - b9ad38d: *Improved search options. Now matches location metadata not just items. REGEX, All words, Any words.*
 - d796423: *change from shields.io to self-hosted CSS pill badges*
 - 3a9be34: *Add date, commit message and modified flag to Git Revision. Also removed default config... Readme is enough.*

**2022-10-23**

 - 7325393: *Add Git Revision to footer to aid in any future troubleshooting.*
 - 132e7b5: *Another readme improvement (discussions) and link to github in app footer*
 - 60e1b80: *Add screenshots to Readme*
 - dd71001: *Fix Readme logo*
 - 8669e58: *Initial working version. Readme still immature.*

