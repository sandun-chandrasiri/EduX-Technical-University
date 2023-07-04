"""
@author: Sandun Chandrasiri
"""
from flask import Flask, render_template, request
import key_config as keys
import boto3 
from boto3.dynamodb.conditions import Key, Attr
import dynamodb_handler as dynamodb
from operator import itemgetter

app = Flask(__name__)

dynamodb = boto3.resource(
    'dynamodb',
    region_name = keys.REGION_NAME,
)

@app.route('/')
def index():

    table = dynamodb.Table('users')

    response = table.scan(ProjectionExpression='email, registration_no, #name', ExpressionAttributeNames={'#name': 'name'})

    if 'Items' in response:
        users = response['Items']
        sorted_users = sorted(users, key=itemgetter('registration_no'))  # Sort the users by registration_no
        return render_template('index.html', users=sorted_users)

    return 'No users found'


@app.route('/signup-success', methods=['post'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        registration_no = request.form['registration-no']
        email = request.form['email']
        degree = request.form['degree']
        contact_no = request.form['contact-no']
        introduction = request.form['introduction']
        gpa = request.form['gpa']
        skills = request.form['skills']
        password = request.form['password']
        
        table = dynamodb.Table('users')
        
        table.put_item(
            Item={
        'name': name,
        'registration_no':registration_no,
        'email': email,
        'degree' : degree,
        'contact-no' : contact_no,
        'introduction' : introduction,
        'gpa' : gpa,
        'skills' : skills,
        'password': password
            }
        )
        success_msg = "Registration Complete. Please Login to your account !"
        error_msg = "Please try AGAIN !"
        return render_template('login.html',success_msg = success_msg)
    return render_template('login.html', error_msg = error_msg)

@app.route('/login')
def login():    
    return render_template('login.html')
    
@app.route('/edit')
def edit():
    return render_template('profile.html')
    
@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/profile-edit',methods = ['post'])
def check():
    if request.method=='POST':

        email = request.form['email']
        password = request.form['password']
        
        table = dynamodb.Table('users')
        response = table.query(
                KeyConditionExpression=Key('email').eq(email)
        )
        items = response['Items']
        name = items[0]['name']
        registration_no = items[0]['registration_no']
        email = items[0]['email']
        degree = items[0]['degree']
        contact_no = items[0]['contact-no']
        gpa = items[0]['gpa']
        introduction = items[0]['introduction']
        skills = items[0]['skills']
        
        print(items[0]['password'])
        
        if password == items[0]['password']:
            
            return render_template("profile.html", registration_no = registration_no, email = email, name = name, contact_no = contact_no, degree = degree, gpa = gpa, skills = skills, introduction = introduction )
                
    invalid_msg = "Invalid Credentials !"        
    return render_template("login.html", invalid_msg = invalid_msg)


@app.route('/profile-edit/<string:email>', methods=['PUT'])
def update_data(email):

    data = request.get_json()
    table = dynamodb.Table('users')
    
    response = table.update_item(
        Key={
            'email': email
        },
        UpdateExpression='SET #name = :name, #contact_no = :contact_no, #degree = :degree, #gpa = :gpa, #skills = :skills, #intro = :introduction',
        ExpressionAttributeNames={
            '#name': 'name',
            '#contact_no': 'contact_no',
            '#degree': 'degree',
            '#gpa': 'gpa',
            '#skills': 'skills',
            '#intro': 'introduction'
        },
        ExpressionAttributeValues={
            ':name': data['name'],
            ':contact_no': data['contact_no'],
            ':degree': data['degree'],
            ':gpa': data['gpa'],
            ':skills': data['skills'],
            ':introduction': data['introduction']
        },
        ReturnValues='ALL_NEW'  
    )

    if (response['ResponseMetadata']['HTTPStatusCode'] == 200):
        return {
            'msg'                : 'Updated successfully',
            'ModifiedAttributes' : response['Attributes'],
            'response'           : response['ResponseMetadata']
        }

    return {
        'msg'      : 'Some error occured',
        'response' : response
    }       

@app.route('/profile/<string:registration_no>')
def viewProfileCard(registration_no):
    table = dynamodb.Table('users')

    response = table.scan(
        FilterExpression=Attr('registration_no').eq(registration_no)
    )

    if 'Items' in response and len(response['Items']) > 0:
        user = response['Items'][0]
        return render_template('public-profile.html', user=user)

    return 'User not found'


if __name__ == '__main__':
    app.run()
    #app.run(debug=True,port=8080,host='0.0.0.0')
