import json, yaml, random
import string, os, re, time
from datetime import datetime, timezone
from flask import Flask, request, Response, abort, render_template, redirect, url_for, send_from_directory, session, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from flask_qrcode import QRcode
import traceback, sys
from git import Repo
import requests
from io import BytesIO

base_path = os.path.dirname(os.path.realpath(__file__))

# GITHUB REPO INFO
repo = Repo.init(base_path)
active_branch = repo.active_branch
current_commit = repo.head.commit
current_commit_datetime = repo.head.commit.committed_datetime
current_commit_message = repo.head.commit.message
dirty_repo = repo.is_dirty()

# GITHUB REPO COMMITS
r = requests.get('https://api.github.com/repos/danricho/where_the/commits')
GHrepo = r.json()
GH_head_datetime = datetime.strptime(GHrepo[0]['commit']['author']['date'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

# COMPARE LOCAL TO GITHUB
if str(GHrepo[0]['sha']) == str(current_commit):
  if dirty_repo:
    local_GH = ("Same version as GitHub", True)
  else:
    local_GH = ("Same version as GitHub", False)
elif GH_head_datetime > current_commit_datetime:
  if dirty_repo:
    local_GH = ("Newer version on GitHub", True)
  else:
    local_GH = ("Newer version available on GitHub", False)
else:
  if dirty_repo:
    local_GH = ("Local version is newer than GitHub", True)
  else:
    local_GH = ("Local version is newer than GitHub", False)

git_revision = {
  "hash": f"{current_commit}"[:7],
  "timestamp": current_commit_datetime.strftime("%Y-%m-%d %H:%M:%S"),
  "subject": current_commit_message,
  "modified": dirty_repo,
  "local_GH": local_GH
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
def to_rgba(col_string):

  def clamp(value, min_value, max_value):
    return max(min_value, min(max_value, value))

  def saturate(value):
    return clamp(value, 0.0, 1.0)

  def hue_to_rgb(h):
    r = abs(h * 6.0 - 3.0) - 1.0
    g = 2.0 - abs(h * 6.0 - 2.0)
    b = 2.0 - abs(h * 6.0 - 4.0)
    return saturate(r), saturate(g), saturate(b)

  def hsl_to_rgb(h, s, l):
    r, g, b = hue_to_rgb(h)
    c = (1.0 - abs(2.0 * l - 1.0)) * s
    r = (r - 0.5) * c + l
    g = (g - 0.5) * c + l
    b = (b - 0.5) * c + l
    return r, g, b

  col_string = col_string.replace(" ", "").strip().lower()
  m = re.match(r"^(#[0-9a-f]{3}|(#)(?:[0-9a-f]{2}){2,4}|(rgb|hsl)(a?)\(([^)]+)\))$", col_string)

  if m.group(1)[0] == "#":
    s = m.group(1).lstrip("#")
    if len(s) == 3:
        r = int(s[0]+s[0], 16)
        g = int(s[1]+s[1], 16)
        b = int(s[2]+s[2], 16)  
        a = 1.0
    elif len(s) == 6:
        r = int(s[0:2], 16)
        g = int(s[2:4], 16)
        b = int(s[4:6], 16) 
        a = 1.0 
    elif len(s) == 8:
        r = int(s[0:2], 16)
        g = int(s[2:4], 16)
        b = int(s[4:6], 16) 
        a = round(int(s[6:8], 16) / 255.0,2)
    return {"r": r, "g": g, "b": b, "a": a}

  elif m.group(3) == "rgb":
    if m.group(4) == "a":
        r,g,b,a = m.group(5).split(',') 
    else:
        a = 1.0
        r,g,b = m.group(5).split(',')
    
    if r[-1] == "%":
        r = round(float(r.rstrip("%"))*2.55)
    else:
        r = int(r)
    if g[-1] == "%":
        g = round(float(g.rstrip("%"))*2.55)
    else:
        g = int(g)
    if b[-1] == "%":
        b = round(float(b.rstrip("%"))*2.55)
    else:
        b = int(b)
    a = float(a)
    return {"r": r, "g": g, "b": b, "a": a}

  elif m.group(3) == "hsl":
    if m.group(4) == "a":
        h,s,l,a = m.group(5).split(',') 
    else:
        a = 1.0
        h,s,l = m.group(5).split(',')

    h = int(h)/360.0
    s = int(s.rstrip("%"))/100.0
    l = int(l.rstrip("%"))/100.0     
    
    r,g,b = hsl_to_rgb(h,s,l)
    a = float(a)
    return {"r": round(r*255), "g": round(g*255), "b": round(b*255), "a": round(a,2)}
      
  print("NOTHING")
  return m.group(3,4,5)

config = {}
load_config()

# THIS SECTION IS TO UPDATE PREVIOUS VERSIONS OF CONFIG.YML
config['PRIMARY-COLOR'] = config.get('PRIMARY-COLOR', '#C0A890')
config['PRINT_TEMPLATE'] = config.get('PRINT_TEMPLATE', {'ADD_DESCRIPTION_TO_LABEL': True, 'ADD_LOGO_TO_QR': True, 'DESCRIPTION_FONT_SIZE': '0.35cm', 'IDENTIFIER': 'AVERY L7164', 'ID_FONT_SIZE': '0.8cm', 'LABEL': {'HEIGHT': '7.2cm', 'WIDTH': '6.353cm', 'X_GUTTER': '0.25cm', 'X_PADDING': '0.25cm', 'Y_GUTTER': '0cm', 'Y_PADDING': '0.1cm'}, 'LABELS_PER_PAGE': 12, 'PAGE': {'WIDTH': '21cm', 'X_MARGIN': '0.7214cm', 'Y_MARGIN': '0.457cm'}, 'QR_HEIGHT': '4.3cm'})
if config.get('DISABLE-QR-LOGO', None) != None: # moving into PRINT_TEMPLATE
  config['PRINT_TEMPLATE']['ADD_LOGO_TO_QR'] = not config.get('DISABLE-QR-LOGO')
  del(config['DISABLE-QR-LOGO'])
if config.get('ADD-DESCRIPTION-TO-QR', None) != None: # moving into PRINT_TEMPLATE
  config['PRINT_TEMPLATE']['ADD-DESCRIPTION-TO-LABEL'] = config.get('ADD-DESCRIPTION-TO-QR')
  del(config['ADD-DESCRIPTION-TO-QR'])
if config['USERS'].get("default", None) == None:
  config['USERS']["default"] = {}
if config['PRINT_TEMPLATE'].get('COLORED_BACKGROUNDS', None) == None:
  config['PRINT_TEMPLATE']['COLORED_BACKGROUNDS'] = True

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
app.config['LOGIN_DISABLED'] = (config['AUTHENTICATION'] not in ["FLASK-LOGIN", "AUTHELIA"])

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
  for loc in locs:
    locs[loc]['items'] = [x.strip() for x in locs[loc]['items']]
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

def props(x):
    return dict((key, getattr(x, key)) for key in dir(x) if key not in dir(x.__class__))

class User(UserMixin):
  def __init__(self, username, password, email=None):
    self.username = username
    self.password = password
    self.email = email
    self.id = username
users = []
for username in config['USERS']:
  users.append(User(username, config['USERS'][username].get('password', 'UNSET'), config['USERS'][username].get('email', None)))

sort_descriptions = ["Location", "Fullness", "Description", "Last Updated", "Type", "ID"]

############################################################
#           DECORATED FUNCTIONS FOR FLASK-LOGIN            #
############################################################

# Loads a user from the active session if it exists.
# Without this you would have to keep logging in.
@login_manager.user_loader
def load_user(username):

  global config

  if config['AUTHENTICATION'] == "FLASK-LOGIN":
    for user in users:
      if user.username == username.lower():
        user.name = user.username
        user.type = "FLASK-LOGIN"
        return user
 
  if config['AUTHENTICATION'] == "AUTHELIA":
    try:
      username = request.headers.get('Remote-User').lower()
      email = request.headers.get('Remote-Email').lower()
      name = request.headers.get('Remote-Name').lower()
      for user in users:
        if user.username == username.lower():
          user.name = user.username
          user.type = "AUTHELIA"
          return user

      # AUTHELIA USER WASN'T IN CONFIG... ADD
      load_config()
      config['USERS'][username] = {'password': 'AUTHELIA', 'email': email}
      save_config()
      users.append(User(username, 'AUTHELIA', email))
      users[-1].name = name
      users[-1].type = "AUTHELIA"
      return users[-1]

    except:      
      return None

  return None # no user found!

# Send un-logged-in users to the login page
@login_manager.unauthorized_handler
def unauthorized():
  return redirect(url_for("login"))

# Serve the login form or process the authorisation on login submission
# TODO: Redirect to original page after login 
@app.route(config['SITE']['PATH_PREFIX'] + '/login', methods=['GET', 'POST'])
def login():

  if config['AUTHENTICATION'] not in ["FLASK-LOGIN", "AUTHELIA"]:
    return redirect(url_for("home"))

  if config['AUTHENTICATION'] == "FLASK-LOGIN":
    if request.method == 'POST':
      username = request.form.get('username', None)
      password = request.form.get('password', None)
      for user in users:
        if username.lower() == user.username.lower() and password == user.password:
          user.type = "FLASK-LOGIN"
          login_user(user)
          return redirect(url_for("home"))
      return abort(401)
    else:
      return render_template('login.j2.html')

  if config['AUTHENTICATION'] == "AUTHELIA":
    try:
      username = request.headers.get('Remote-User').lower()
      email = request.headers.get('Remote-Email').lower()
      name = request.headers.get('Remote-Name').lower()
      for user in users:
        if user.username == username.lower():
          user.type = "AUTHELIA"
          login_user(user)          
          return redirect(url_for("home"))

      # AUTHELIA USER WASN'T IN CONFIG... ADD
      load_config()
      config['USERS'][username] = {'password': 'AUTHELIA', 'email': email}
      save_config()
      users.append(User(username, 'AUTHELIA', email))
      users[-1].name = name
      users[-1].type = "AUTHELIA"
      return redirect(url_for("home"))
    except:      
      return abort(401)
  return abort(401)

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
  return redirect(url_for("list_locs")) 
  
# list locations
@app.route(config['SITE']['PATH_PREFIX'] + '/list')
@login_required
def list_locs():
  load_json()   

  # THIS IS FOR WHEN AUTH IS NO_AUTH.
  if current_user.is_anonymous:
     current_user.username = "DEFAULT"

  # SORTING
  if config['AUTHENTICATION'] == "NO-AUTH":
    username = "DEFAULT"

  sorting = 0 # default sort to location
  load_config()
  for user in config['USERS']:
    if current_user.username.lower() == user.lower():
      sorting = config['USERS'][user].get("LOCATION_SORTING", 0)

  # print(list(locs.values())[0])
  if sort_descriptions[sorting] == "Location":    
    sorted_locs = list(sorted(locs.values(), key=lambda i: (i['location'], i['description'])))
    # print([(i['location'], i['description']) for i in sorted_locs])
  elif sort_descriptions[sorting] == "ID":
    sorted_locs = list(sorted(locs.values(), key=lambda i: (i['id'])))
    # print([(i['id']) for i in sorted_locs])
  elif sort_descriptions[sorting] == "Fullness":
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

  # PAGINATION
  items_per_page = 10
  for user in config['USERS']:
    if current_user.username.lower() == user.lower():
      items_per_page = config['USERS'][user].get("LOCATIONS_PER_PAGINATED_PAGE", 10)

  page = request.args.get('page', 1, type=int)
  page = max(page, 1) # has to be minimum 1
  pages = round(len(sorted_locs)/items_per_page + .499)   
  page = min(page, pages) # has to be at most the last page
  from_page = int(page) * items_per_page - items_per_page
  upto_page = int(page) * items_per_page
  upto_page = min(upto_page, len(sorted_locs))
  pagination_info = { "pages": pages, "current_page": page, "first": from_page, "last": upto_page, "total": len(sorted_locs), "per_page": items_per_page }
  sorted_locs = sorted_locs[from_page:upto_page]

  # Friendlier Timestamps  
  for loc in sorted_locs:
    loc['last_change'] = datetime.fromtimestamp(loc['last_change']).strftime("%-I:%M %p, %d %B %Y")

  return render_template('list.j2.html', locs=sorted_locs, sorted_str=sort_descriptions[sorting], SITE=config['SITE'], pagination=pagination_info )

@app.route(config['SITE']['PATH_PREFIX'] + '/search', methods=['GET', 'POST'])
@login_required
def search():
  if request.method == "GET": # FORM ONLY  
    return render_template('search.j2.html', form_data={}, results=None)

  else: # SEARCH FUNCTION
    submit_data = dict(request.form)
    return render_template('search.j2.html', form_data=submit_data, results=search_locs(submit_data['search-input'], mode=submit_data["search-mode-select"])) 

@app.route(config['SITE']['PATH_PREFIX'] + '/set-setting/<string:setting>/<string:value>/<string:next_endpoint>')
@login_required
def set_setting(setting, value, next_endpoint):

  load_config()
  global config

  # THIS IS FOR WHEN AUTH IS NO_AUTH.
  if current_user.is_anonymous:
     current_user.username = "DEFAULT"

  for user in config['USERS']:
    if current_user.username.lower() == user.lower():
      
      if setting == "sort":
        config['USERS'][user]["LOCATION_SORTING"] = sort_descriptions.index(value)
        save_config()

      if setting == "per_page":
        config['USERS'][user]["LOCATIONS_PER_PAGINATED_PAGE"] = int(value)
        save_config()

  return redirect(url_for(next_endpoint)) 

@app.route(config['SITE']['PATH_PREFIX'] + '/scan/<string:url_id>')
@login_required
def scanned(url_id):
  load_json()
  if url_id.upper() in locs:
    return redirect(url_for("view", url_id=url_id)) 
  else:
    raise locationIdNotFound()

# view a location page
@app.route(config['SITE']['PATH_PREFIX'] + '/view/<string:url_id>')
@login_required
def view(url_id):  
  load_json()
  from_search = False
  if request.referrer:
    from_search = config['SITE']['PATH_PREFIX'] + '/search' in request.referrer
  if url_id.upper() in locs:
    locs[url_id.upper()]['last_change'] = datetime.fromtimestamp(locs[url_id.upper()]['last_change']).strftime("%-I:%M %p, %d %B %Y")
    return render_template('view.j2.html', loc=locs[url_id.upper()], from_search=from_search)
  else:
    raise locationIdNotFound()

# print qr code for location page
@app.route(config['SITE']['PATH_PREFIX'] + '/print/<string:url_id>')
@login_required
def print_qr(url_id):
  load_config()
  load_json()
  if url_id.upper() in locs:
    return render_template('print.j2.html', locs=[locs[url_id.upper()]], SITE=config['SITE'], batch=False, template=config['PRINT_TEMPLATE'])
  else:
    raise locationIdNotFound()

# print qr code for location page
@app.route(config['SITE']['PATH_PREFIX'] + '/batch-print/')
@login_required
def print_batch():
  load_config()
  load_json()
  return render_template('print.j2.html', locs=locs.values(), SITE=config['SITE'], batch=True, template=config['PRINT_TEMPLATE'])

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
    save_data['sealed'] = {"on": True, 'off': False}[save_data.get('sealed', 'off')]
    del save_data['add-item-input']
    # print(locs[url_id])
    print(save_data)
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

@app.route(config['SITE']['PATH_PREFIX'] + '/export/')
@login_required
def export_csv():
  load_json()   
  dataCSV = "ID,Type,Description,Location,Destination,Sealed\n"
  for item in locs.values():
    dataCSV += f"{item['id']},{item['type']},{item['description']},{item['location']},{item.get('destination','')},{item.get('sealed','')}\n"  
  return send_file(
    BytesIO(dataCSV.encode()),
    mimetype="text/csv",
    download_name ="export.csv"
  )



# serve static files
@app.route(config['SITE']['PATH_PREFIX'] + '/static/<path:path>')
def send_static(path):
  if config['SITE']['PATH_PREFIX'] != "":
    if path in ["icons/browserconfig.xml", "icons/site.webmanifest"]:
      with open(base_path + f'/static/{path}', 'r') as f:
        if path in ["icons/browserconfig.xml"]:
          return Response(f.read().replace('"/static',f'"{config["SITE"]["PATH_PREFIX"]}/static'), mimetype='text/xml')
        if path in ["icons/site.webmanifest"]:
          return Response(f.read().replace('"/static',f'"{config["SITE"]["PATH_PREFIX"]}/static'), mimetype='application/manifest+json')
  
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
    'PRIMARY_COLOR_RGB': to_rgba(config['PRIMARY-COLOR']),
    'request_info': request.headers,
    'user': props(current_user),
    'path': request.path,
    'SITE': config['SITE'],
    'STATS': { "LOCS": len(locs.values()), "ITEMS": len(sum([loc['items'] for loc in locs.values()],[])) },
    'AUTHELIA_URL': config.get('AUTHELIA_URL', None),
  }

############################################################
#                  START THE FLASK APP!                    #
############################################################

if __name__ == '__main__':    
  app.run(host=config['FLASK']['HOST'], port=config['FLASK']['PORT'], use_reloader=config['FLASK']['USE_RELOADER'], debug=config['FLASK']['DEBUG'])




