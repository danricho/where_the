from fcntl import F_ADD_SEALS
import json, yaml, random
import string, os, re, time, subprocess
import qrcode, qrcode.image.svg
from datetime import datetime, date
from flask import Flask, request, Response, abort, render_template, redirect, url_for, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from flask_qrcode import QRcode
import traceback, sys

base_path = os.path.dirname(os.path.realpath(__file__))
git_revision = {
  "hash": subprocess.check_output(["git", "show", "-s", "--format=%h"], cwd=os.path.dirname(os.path.abspath(__file__))).strip().decode(),
  "timestamp": subprocess.check_output(["git", "show", "-s", "--format=%cd", "--date=format:%Y-%m-%d %H:%M:%S"], cwd=os.path.dirname(os.path.abspath(__file__))).strip().decode(),
  "subject": subprocess.check_output(["git", "show", "-s", "--format=%s"], cwd=os.path.dirname(os.path.abspath(__file__))).strip().decode(),
  "modified": bool(len(subprocess.check_output(["git", "diff"], cwd=os.path.dirname(os.path.abspath(__file__))).strip().decode()))
}

############################################################
#              LOADING CONFIG FROM YAML FILE               #
############################################################

def load_config():
  global config
  with open(base_path + "/config.yml", "r") as f:
    config = yaml.safe_load(f)
def save_config():
  with open(base_path + "/config.yml", "w") as f:
    yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

config = {}
load_config()

# done this way for backward compatibility of config.yml and to create defaults
config['PRIMARY-COLOR'] = config.get('PRIMARY-COLOR', '#C0A890') 
config['DISABLE-QR-LOGO'] = config.get('DISABLE-QR-LOGO', False)
config['ADD-DESCRIPTION-TO-QR'] = config.get('ADD-DESCRIPTION-TO-QR', False)
save_config()

############################################################
#                   INITIALISE FLASK APP                   #
############################################################

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = config['FLASK']['TEMPLATES_AUTO_RELOAD'] 
app.config['SECRET_KEY'] = config['FLASK']['SECRET']
QRcode(app)

login_manager = LoginManager()
login_manager.init_app(app)
app.config['LOGIN_DISABLED'] = config['FLASK']['LOGIN_DISABLED'] 

############################################################
#                    LOAD INITIAL DATA                     #
############################################################

# TODO: ADD OPTION FOR TINYDB / YAML / JSON STORAGE

locs = {}
def load_json():
  global locs
  try:
    with open(base_path + '/data.json', 'r') as openfile:
      locs = json.load(openfile)
  except:
    print("No data file... creating blank")
    save_json()
  daily_backup()
# backup will only occur if the site is being used...
def daily_backup():
  max_backups = 14
  backup_datetime_format = "%Y-%m-%d"
  backups_directory = 'data_bkp/'
  today_bkp_filename = f'{datetime.now().strftime(backup_datetime_format)}_data.bkp.json'
  if not os.path.exists(f'{base_path}/{backups_directory}{today_bkp_filename}'):
    with open(f'{base_path}/{backups_directory}{today_bkp_filename}', 'w') as outfile:
      outfile.write(json.dumps(locs, indent=4))
  files = sorted([f for f in os.listdir(f'{base_path}/{backups_directory}') if "bkp" in f])
  while len(files) > max_backups:
    os.remove(f'{base_path}/{backups_directory}{files[0]}')
    files = sorted([f for f in os.listdir(f'{base_path}/{backups_directory}') if "bkp" in f])
def save_json():
  with open(base_path + '/data.json', 'w') as outfile:
    outfile.write(json.dumps(locs, indent=4))
load_json()

############################################################
#             FUNCTION TO CREATE NEW LOCATION              #
############################################################

def new_loc():  

  global locs
  load_json()

  def create_id():
    loc_id = random.choice(string.ascii_letters)
    loc_id += random.choice(string.ascii_letters)
    loc_id += random.choice(string.ascii_letters)
    loc_id += str(random.randint(0, 9))
    loc_id += str(random.randint(0, 9))
    loc_id += str(random.randint(0, 9))
    return loc_id.upper()

  loc_id = None
  while loc_id == None or loc_id in locs:
    loc_id = create_id()
  
  loc_info = {
    "id": loc_id,
    "description": "",
    "type": "",
    "location": "", 
    "items": [],
    "fullness": 0,
    "last_change": time.time()
  }
  locs[loc_id] = loc_info
  print(f"Created location: {loc_id}")
  save_json()
  return loc_id

############################################################
#              FUNCTION TO TEXT SEARCH ITEMS               #
############################################################

def search_locs(term, mode="any"):  

  global locs
  load_json()

  results = {}
  term = term.upper().strip()

  if mode in ["any", "all"]:
    term = re.sub(r'[^a-zA-Z0-9 ]+', ' ', term, flags=re.IGNORECASE)
    term = term.split()    

  for loc in list(locs.values()):
    this_id = loc['id'] 
    if mode in ["any", "all"]:
      word_pool = str(list(loc.values()))
      word_pool = re.sub(r'[^a-zA-Z0-9 ]+', ' ', word_pool, flags=re.IGNORECASE)    
      word_pool = " ".join(word_pool.split()).upper()     

    if mode == "any":
      if any(x in word_pool for x in term):
        if this_id not in results:
          results[this_id] = dict(loc)
          results[this_id]['items'] = []
      matching_items = [item for item in loc['items'] if any(x in item.upper() for x in term)]
      if len(matching_items):
        if this_id not in results:
          results[this_id] = dict(loc)
          results[this_id]['items'] = []
        results[this_id]['items'] = matching_items
      
    elif mode == "all":
      if all(x in word_pool for x in term):
        if this_id not in results:
          results[this_id] = dict(loc)
          results[this_id]['items'] = []
      matching_items = [item for item in loc['items'] if any(x in item.upper() for x in term)]
      if len(matching_items):
        if this_id not in results:
          results[this_id] = dict(loc)
          results[this_id]['items'] = []
        results[this_id]['items'] = matching_items

    elif mode == "re":
      word_pool = str(list(loc.values())).upper()
      if re.search(term, word_pool):
        results[this_id] = dict(loc)
        results[this_id]['items'] = []
      for item in loc['items']:
        if re.search(term, item.upper()):
          if this_id not in results:
            results[this_id] = dict(loc)
            results[this_id]['items'] = []
          results[this_id]['items'].append(item)

  return {"search": (mode, term), "results": list(results.values())}

############################################################
# EXCEPTION FOR FLASK REQUESTS WITH NOT MATCHING LOCATION  #
############################################################

class locationIdNotFound(Exception):
    """Exception raised when ID not found in location data."""
    def __init__(self):
        self.code = 500
        self.name = "Location Not Found"
        self.description = "The location ID was not found in the location data."        
        super().__init__(self.description)

############################################################
#               SET UP USER FOR FLASK-LOGIN                #
############################################################

class User(UserMixin):
  def __init__(self, id, username, password):
    self.id = id
    self.username = username
    self.password = password
users = []
for id in config['USERS']:
  users.append(User(id, config['USERS'][id]['username'], config['USERS'][id]['password']))

############################################################
#           DECORATED FUNCTIONS FOR FLASK-LOGIN            #
############################################################

# Loads a user from the active session if it exists.
# Without this you would have to keep logging in.
@login_manager.user_loader
def load_user(id):
  id = int(id)
  for user in users:
    if user.id == id:
      return user
  return None # no user found!

# Send un-logged-in users to the login page
@login_manager.unauthorized_handler
def unauthorized():
  return redirect(url_for("login"))

# Serve the login form or process the authorisation on login submission
# TODO: Redirect to original page after login 
# TODO: Remember user
@app.route(config['SITE']['PATH_PREFIX'] + '/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    username = request.form.get('username', None)
    password = request.form.get('password', None)
    for user in users:
      if username == user.username and password == user.password:
        login_user(user)
        return redirect(url_for("home"))
    return abort(401)
  else:
    return render_template('login.j2.html')

# URL to log out
@app.route(config['SITE']['PATH_PREFIX'] + '/logout')
def logout():
  logout_user()
  return redirect(url_for("login"))

############################################################
#    DECORATED FUNCTIONS FLASK ROUTING AND PAGE SERVING    #
############################################################

# home page
@app.route(config['SITE']['PATH_PREFIX'] + '/')
@login_required
def home():
  global locs
  load_json()    

  username = ""
  load_config()
  for id in config['USERS']:
    if hasattr(current_user, 'username'):
      username = current_user.username
  
  return render_template('home.j2.html', SITE=config['SITE'], username=username)
  
sort_descriptions = ["Location", "% Full", "Description", "Last Updated", "Type", "ID"]
# list locations
@app.route(config['SITE']['PATH_PREFIX'] + '/list')
@login_required
def list_locs():
  global locs
  load_json()    

  sorting = 0 # default sort to location
  load_config()
  for id in config['USERS']:
    if hasattr(current_user, 'username'):
      if current_user.username == config['USERS'][id]['username']:
        sorting = config['USERS'][id].get("LOCATION_SORTING", 0)

  # print(list(locs.values())[0])
  if sort_descriptions[sorting] == "Location":    
    sorted_locs = list(sorted(locs.values(), key=lambda i: (i['location'], i['description'])))
    # print([(i['location'], i['description']) for i in sorted_locs])
  elif sort_descriptions[sorting] == "ID":
    sorted_locs = list(sorted(locs.values(), key=lambda i: (i['id'])))
    # print([(i['id']) for i in sorted_locs])
  elif sort_descriptions[sorting] == "% Full":
    sorted_locs = list(sorted(locs.values(), key=lambda i: (-i['fullness'], i['description'])))
    # print([(i['fullness'], i['description']) for i in sorted_locs])
  elif sort_descriptions[sorting] == "Description":
    sorted_locs = list(sorted(locs.values(), key=lambda i: (i['description'])))
    # print([(i['description']) for i in sorted_locs])
  elif sort_descriptions[sorting] == "Last Updated":
    sorted_locs = list(sorted(locs.values(), key=lambda i: (i['last_change']), reverse=True))
    # print([(i['last_change']) for i in sorted_locs])
  elif sort_descriptions[sorting] == "Type":
    sorted_locs = list(sorted(locs.values(), key=lambda i: (i['type'])))
    # print([(i['last_change']) for i in sorted_locs])

  for loc in sorted_locs:
    loc['last_change'] = datetime.fromtimestamp(loc['last_change']).strftime("%-I:%M %p, %d %B %Y")

  return render_template('list.j2.html', locs=sorted_locs, sorted_str=sort_descriptions[sorting], SITE=config['SITE'])

@app.route(config['SITE']['PATH_PREFIX'] + '/search', methods=['GET', 'POST'])
@login_required
def search():
  if request.method == "GET": # FORM ONLY  
    return render_template('search.j2.html', form_data={}, results=None)

  else: # SEARCH FUNCTION
    submit_data = dict(request.form)
    return render_template('search.j2.html', form_data=submit_data, results=search_locs(submit_data['search-input'], mode=submit_data["search-mode-select"])) 

@app.route(config['SITE']['PATH_PREFIX'] + '/cycle-sort')
@login_required
def cycle_sort():
  load_config()
  global config
  for id in config['USERS']:
    if current_user.username == config['USERS'][id]['username']:
      if "LOCATION_SORTING" not in config['USERS'][id]:
        config['USERS'][id]["LOCATION_SORTING"] = 1
      else:
        config['USERS'][id]["LOCATION_SORTING"] += 1
        if config['USERS'][id]["LOCATION_SORTING"] == len(sort_descriptions):
          config['USERS'][id]["LOCATION_SORTING"] = 0
  save_config()
  return redirect(url_for("list_locs")) 

@app.route(config['SITE']['PATH_PREFIX'] + '/scan/<string:url_id>')
@login_required
def scanned(url_id):
  global locs
  load_json()
  if url_id.upper() in locs:
    return redirect(url_for("view", url_id=url_id)) 
  else:
    raise locationIdNotFound()

# view a location page
@app.route(config['SITE']['PATH_PREFIX'] + '/view/<string:url_id>')
@login_required
def view(url_id):
  global locs
  load_json()
  if url_id.upper() in locs:
    locs[url_id.upper()]['last_change'] = datetime.fromtimestamp(locs[url_id.upper()]['last_change']).strftime("%-I:%M %p, %d %B %Y")
    return render_template('view.j2.html', loc=locs[url_id.upper()])
  else:
    raise locationIdNotFound()

# print qr code for location page
@app.route(config['SITE']['PATH_PREFIX'] + '/print/<string:url_id>')
@login_required
def print_qr(url_id):
  global locs
  load_json()
  if url_id.upper() in locs:
    return render_template('print.j2.html', loc=locs[url_id.upper()], SITE=config['SITE'])
  else:
    raise locationIdNotFound()

# edit location page (serve form and process submission)
@app.route(config['SITE']['PATH_PREFIX'] + '/edit/<string:url_id>', methods=['GET', 'POST'])
@login_required
def edit(url_id):
  global locs
  load_json()

  if request.method == "POST":    
    save_data = dict(request.form)
    save_data['items-list'] = json.loads(save_data['items-list'])
    save_data['fullness-input'] = int(save_data['fullness-input'])
    del save_data['add-item-input']
    # print(locs[url_id])
    # print(save_data)
    for key in save_data:
      locs[url_id][key.replace("-input","").replace("-list","")] = save_data[key]
    locs[url_id]["last_change"] = time.time()
    save_json()
    return redirect(url_for('view', url_id=url_id)) 

  else:    
    if url_id.upper() in locs:
      return render_template('edit.j2.html', loc=locs[url_id.upper()])
    else:
      raise locationIdNotFound()
 
# create a new location page (redirects to edit once ID generated)
@app.route(config['SITE']['PATH_PREFIX'] + '/create', methods=['GET', 'POST'])
@login_required
def create():  
  return redirect(url_for('edit', url_id=new_loc())) 
  
# delete location URL (redirect home if successful)
@app.route(config['SITE']['PATH_PREFIX'] + '/delete/<string:url_id>')
@login_required
def delete(url_id):
  global locs
  load_json()
  if url_id.upper() in locs:
    del locs[url_id.upper()]
    save_json()  
    return redirect(url_for('home')) 
  else:
    raise locationIdNotFound()

# serve static files
@app.route(config['SITE']['PATH_PREFIX'] + '/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

# error page generator - comment decortaor to see errors in terminal
@app.errorhandler(Exception)
def handle_error(e):

  error_info = {}
  try:
    error_info['code'] = e.code
  except:
    pass
  try:
    error_info['name'] = e.name
  except:
    pass
  try:
    error_info['description'] = e.description
  except:
    pass  
  
  if error_info == {}:
    etype, value, tb = sys.exc_info()
    try:
      error_info['code'] = etype.__name__
    except:
      pass
    try:
      error_info['name'] = value
    except:
      pass
    try:
      error_info['description'] = traceback.format_exc().replace('\n', '<br/>')
    except:
      pass  
  
  return render_template('error.j2.html', error=error_info)

# DATA PROVIDED TO ALL TEMPLATES
@app.context_processor
def inject_data():    
  return {
    'git_revision': git_revision,
    'PRIMARY_COLOR': config['PRIMARY-COLOR'],
    'DISABLE_QR_LOGO': config['DISABLE-QR-LOGO'],      
    'ADD_DESCRIPTION_TO_QR': config['ADD-DESCRIPTION-TO-QR'],    
  }


############################################################
#                  START THE FLASK APP!                    #
############################################################

if __name__ == '__main__':    
  app.run(host=config['FLASK']['HOST'], port=config['FLASK']['PORT'], use_reloader=config['FLASK']['USE_RELOADER'], debug=config['FLASK']['DEBUG'])




