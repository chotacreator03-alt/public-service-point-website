PUBLIC SERVICE POINT — WEBSITE PROJECT
Python + Flask + SQLite | Visual Studio Code | Windows

FEATURES
- Home page, responsive layout, services grouped in separate tables
- Admin panel: edit shop name, owner, phone, WhatsApp, address, opening hours, about, hero text, Facebook link
- Upload owner photo from Admin settings
- Add/edit/delete services, descriptions, categories, prices and visibility
- Customer reviews are private until Admin approves them
- Contact form messages are saved for Admin to view
- SQLite database creates itself on first run

RUN LOCALLY
1. Install Python 3.10+ from https://www.python.org/downloads/ (tick Add Python to PATH)
2. Open this folder in VS Code
3. Double-click run_windows.bat OR open VS Code Terminal and run:
   py -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   python app.py
4. Visit http://127.0.0.1:5000

FIRST ADMIN LOGIN (LOCAL SETUP ONLY)
Username: admin
Password: ChangeMe123!

IMPORTANT SECURITY NOTES
- Change the default admin password before putting the site on the public internet.
- Set ADMIN_USERNAME and ADMIN_PASSWORD environment variables before first run if you want custom credentials. They are only used when the admin user is first created.
- Set a long random SECRET_KEY environment variable before deployment.
- app.py uses debug=True for local development only. Disable debug and use a production WSGI server for public hosting.
- The website is local-only until you buy/configure hosting and a domain.
- Contact form messages may contain personal information; protect access and delete when no longer needed.
- The site does not claim to be an official government website. Final approval of government applications depends on the relevant authority.

PRE-FILLED SHOP DETAILS
PUBLIC SERVICE POINT | Owner: Sabid Ali
Address: Shivpur, Tapan, Dakshin Dinajpur, West Bengal
Phone/WhatsApp: 8250117043

Update the opening hours and upload your photo in Admin > Website Information.
