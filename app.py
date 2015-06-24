from flask import Flask, redirect, request, Response, session, jsonify
import logging
import time, os, random
import hashlib 
from passlib.hash import sha256_crypt
import ConfigParser
from bson.json_util import dumps
from flask.ext.cors import CORS
import sendgrid
import pprint


# -------------------------------------------
# setup 

# grab some vars from our config file
config = ConfigParser.ConfigParser()
config.readfp(open('config.ini'))

# in case we need to connect to a database and track this stuff
# con = pymongo.Connection( host='localhost' , port=27017 )
# col = con['some_database']

# initialize the application
app = Flask(__name__)

# salt
app.secret_key = config.get('global' , 'salt')

# set up logging ( if needed )
# logging.basicConfig( level=logging.INFO )
# logging is recommended :: when we enter production, turn this on!
# write something that monitors the log (if conditional, do something)

# email config
# sg = sendgrid.SendGridClient( 'app37968798@heroku.com' , 's26z16q97662' )


# -------------------------------------------
# the cors configuration
# this particular one will allow cors requests only for the /cors_test path

whitelist = [
    'www.something.com',
    'http://nothing.com'
]

# CORS( app , resources=r'/email*' , allow_headers = 'Content-Type' )
CORS( app , resources={ r'*' : { 'origins' : whitelist }} , allow_headers = 'Content-Type' )


# -------------------------------------------
# app functions

# simple hashing
def hash_something( something ):
    
    return hashlib.sha512( app.secret_key + something ).hexdigest()


# -------------------------------------------
# routes ( testing )

# tests cross-site responses-
@app.route('/cors_test')
def cors_test():

    return jsonify( output = "success" )


# tests if hashing works
@app.route('/hash_test')
def hash_test():

    output = hash_something( 'my super secret thing' )
    return "\n" + output + "\n\n"


#tesits if automailer works
@app.route('/email_test')
def email_test():

    # populate email with some random, unique crap
    timestamp = str( time.time() )

    # basic message
    message = sendgrid.Mail()
    message.add_to('Marcus Veres <marcus.veres@gmail.com>')
    message.set_subject('SendGrid Example')
    message.set_html( 'html email sent at: ' + timestamp + '\n' )
    message.set_text( 'text-based email sent at: ' + timestamp + '\n' )
    message.set_from('Coca Cola App <no-reply@blooming-earth-1399.herokuapp.com>')

    # send the message
    status, msg = sg.send(message)

    # output something

    # return status - this returns an error 
    # TODO: research the sendgrid documentation 

    return 'attempted to send the email :: code got this far';


# -------------------------------------------
# functions

insults_array = [
    'smells bad',
    'is a dumbass',
    'makes Kim Kardashian look like a goddamn genius',
    'is unable to see why kids love the great taste of Cinnamon Toast Crunch',
    'makes baby Jesus cry',
    'thinks MDMA is a web comic'
        ]

# insult the user
def abuse( arguments ):

    # generate a random whole number
    limit = len( insults_array ) - 1
    insult = insults_array[ random.randint( 0 , limit ) ]

    # concatenate the arguments into a string
    victim = ' '.join( arguments )

    return victim + ' ' + insult + '!'


# -------------------------------------------
# routes ( live )

# some route goes here
@app.route('/slack' , methods=['POST'])
def slack():

    # get the raw post data
    user_input = request.form.get('text')

    return user_input

    # break apart the input into an array
    input_array = user_input.split(' ')

    # the first word of the input is the command
    command = input_array[0]

    # the following words are going to be arguments
    # so we clone the old list, then splice out the first argument
    arguments = list(input_array)
    arguments.pop( 0 )

    # -------------------
    # check the command
    
    if str(command) == 'abuse':
        output = abuse( arguments )
        return output

    return 'does not compute'


# some route goes here
@app.route('/raw' , methods=['POST'])
def raw():

    # get the raw post data
    user_input = request.get_data()

    # break apart the input into an array
    input_array = user_input.split(' ')

    # the first word of the input is the command
    command = input_array[0]

    # the following words are going to be arguments
    # so we clone the old list, then splice out the first argument
    arguments = list(input_array)
    arguments.pop( 0 )

    # -------------------
    # check the command
    
    if str(command) == 'abuse':
        output = abuse( arguments )
        return output

    return 'does not compute'


# create catch-all that sends the user to add_points
#'You want path: %s' % path

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return "you have reached the catch-all :)"


# -------------------------------------------
# all systems go - start the app

if __name__ == '__main__':
    app.run(
        debug = config.get('global','debug'),
        host = config.get('global','host'),
        port = int(config.get('global','port'))
    )


## reference

#    def login(self, request) :
#
#        if not userdata :
#            flash('Login Failed', 'danger')
#            return False
#
#        if sha256_crypt.verify(request.form.get('password'), userdata.get('password')) :
#            session_data = {
#                'email' : userdata.get('email'),
#                'admin' : userdata.get('admin'),
#                'id'    : str(userdata.get('_id'))
#            }
#            session['userdata'] = session_data
#            flash('Login Successful', 'success')
#            return True
#
#        flash('Login Failed', 'danger')

