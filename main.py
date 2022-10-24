import json, yaml, random
import string, os, re, time, subprocess
import qrcode, qrcode.image.svg
from datetime import datetime, date
from flask import Flask, request, Response, abort, render_template, redirect, url_for, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from flask_qrcode import QRcode

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
config = {}
def load_config():
  global config
  with open(base_path + "/config.yml", "r") as f:
    config = yaml.safe_load(f)
load_config()
def save_config():
  with open(base_path + "/config.yml", "w") as f:
    yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

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
  today = date.today().strftime("%Y-%m-%d")
  if not os.path.exists(base_path + f'/data_bkp/{today}_bkp_data.json'):
    with open(base_path + f'/data_bkp/{today}_bkp_data.json', 'w') as outfile:
      outfile.write(json.dumps(locs, indent=4))
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

def find_item(findstr):
  def simple_string(complex_string):
    pattern = re.compile('[^a-z0-9 *?]+', re.IGNORECASE)
    return pattern.sub('', complex_string)
  global locs
  load_json()
  result = {"query": findstr, "results": {}}

  findstr = "*" + findstr + "*"
  findstr = simple_string(findstr)
  findstr = findstr.replace("*", ".*").replace("?", ".")

  result['regex'] = findstr
  regex = re.compile(findstr, re.IGNORECASE)
  
  for loc in locs:
    matching_items = [itm for itm in locs[loc]['items'] if re.match(regex, simple_string(itm))]
    # print(loc, matching_items)
    if len(matching_items):
      result['results'][loc] = locs[loc]
      result['results'][loc]['items'] = matching_items
      result['results'][loc]['match_count'] = len(matching_items)
      matching_items = []
  return result

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

sort_descriptions = ["Location", "% Full", "Description", "Last Updated", "Type", "ID"]
# home page / list locations and search results
@app.route(config['SITE']['PATH_PREFIX'] + '/', methods=['GET', 'POST'])
@login_required
def home():
  if request.method == "GET": # HOME PAGE    
    global locs
    load_json()    
    
    username = ""
    sorting = 0 # default to location

    load_config()
    for id in config['USERS']:
      if hasattr(current_user, 'username'):
        username = current_user.username
        if current_user.username == config['USERS'][id]['username']:
          if "LOCATION_SORTING" in config['USERS'][id]:
            sorting = config['USERS'][id]["LOCATION_SORTING"]
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

    # reverse=True    
    return render_template('home.j2.html', locs=sorted_locs, sorted_str=sort_descriptions[sorting], SITE=config['SITE'], username=username)

  else: # SEARCH FUNCTION    
    search_str = dict(request.form)['search-input']
    return render_template('search.j2.html', results=find_item(search_str), SITE=config['SITE'])    

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
  return redirect(url_for("home")) 

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
  return render_template('error.j2.html', error=error_info)

# DATA PROVIDED TO ALL TEMPLATES
@app.context_processor
def inject_data():    
  return {
    'git_revision': git_revision    
  }


############################################################
#                  START THE FLASK APP!                    #
############################################################

if __name__ == '__main__':    
  app.run(host=config['FLASK']['HOST'], port=config['FLASK']['PORT'], use_reloader=config['FLASK']['USE_RELOADER'], debug=config['FLASK']['DEBUG'])




