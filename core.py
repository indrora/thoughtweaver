from flask import Flask
import os
import configparser
import enum

# we're going to load the configuration from a parsed file

config_file_path = os.environ.get("THOUGHTWEAVER_CONFIG", None)
base_config_path = os.path.join( os.path.dirname(os.path.abspath(__file__)), 'default.ini')

ini_config = configparser.ConfigParser()
ini_config.read_file(open(base_config_path))
if(config_file_path is not None):
    print("Configuration file path is "+config_file_path)
    ini_config.read(config_file_path.split(';'))


app = Flask(__name__)

# read the configuration out
for section in ini_config.sections():
    prefix = section.upper()
    for (key, value) in ini_config.items(section):
        app_config_key = prefix + '_' + key.upper()
        app.config[app_config_key] = value


# Some helper functions in Jinja
@app.template_filter('enum_check')
def jinja_check_enum(obj, maybe_enum_value):
    if( not isinstance(obj, enum.Enum)):
        return False
    if( not isinstance(maybe_enum_value, str)):
        return False
    enum_name = obj.name.lower()
    check_name = maybe_enum_value.lower()
    return check_name == enum_name