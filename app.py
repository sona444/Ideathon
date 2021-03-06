import os, sys, subprocess, platform
from flask import Flask, render_template, request, redirect,url_for, make_response
from flask_migrate import Migrate, MigrateCommand
from flask_sqlalchemy import SQLAlchemy
import json
from flask_mail import Mail, Message
import pdfkit


app = Flask(__name__)
mail = Mail(app)
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://rodltdkolfkcqm:e4b03c73ecc495b993bc38805e52d3d1d04a58ce4f199a31c7a0b5241d08e9c1@ec2-3-213-76-170.compute-1.amazonaws.com:5432/d3604thenjsg37'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'ideathonmriirs1.0@gmail.com'
app.config['MAIL_PASSWORD'] = 'mriirsideathon1.0'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
from models import participants, team

# two decorators, same function
@app.route('/')
def index():
    return render_template("index.html")

# @app.route('/registration')
# def register():
#     return render_template("registrations.html")

# @app.route('/registrations2/<idd>/<members>')
# def register2(members,idd):
#     return render_template("registrations2.html",members=members, id=idd)
   
@app.route('/random1234')
def email():
    return render_template("email.html")

@app.route('/download-it', methods=['GET'])
def downloadd():
    teams=team.query.all()
    participant=participants.query.all()
    usr_list = []
    participant_name=[]
    participant_email=[]
    participant_phone=[]
    participant_organization=[]
    participant_is_leader=[]
    for u in teams:
        m=[]
        n=[]
        o=[]
        p=[]
        q=[]
        usr = {
                    'id': u.id,
                    'team_name': u.team_name,
                    'team_members': u.team_members,
                    'team_type': u.team_type,
                    'problem_statement': u.problem_statement,
        }
        usr_list.append(usr)

        for v in participant:
            if u.id==v.team_id:
                m.append(v.name)
                n.append(v.email)
                o.append(v.phone)
                p.append(v.organization)
                q.append(v.is_leader)
        participant_name.append(m)
        participant_email.append(n)
        participant_phone.append(o)
        participant_organization.append(p)
        participant_is_leader.append(q)
    rendered= render_template("down.html",users=usr_list, participant_name=participant_name,participant_email=participant_email,participant_phone=participant_phone,participant_organization=participant_organization,participant_is_leader=participant_is_leader)
    pdf=pdfkit.from_string(rendered, False)
    response=make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=output.pdf'
    # pdfkit.from_file('templates/attendees.html', 'out.pdf')
    return response 

@app.route('/send-email/<email>/<id>')
def sendem(id,email):
    try :
        emails=list(email.split(','))
        msg = Message(
            'Idea Submission of Team ID '+str(id),
            sender ='ideathonmriirs1.0@gmail.com',
            recipients = emails
            )
        msg.html = '''
            <div>
                Dear participant,<br><br>

                We are pleased to recieve your registration. As a next step kindly prepare a Powerpoint Presentation(PPT) depicting your idea and methodology towards the problem statement chosen.<br>
                We request you to please follow the following format for PPT https://docs.google.com/presentation/d/1jQsCt1jc_SFMeZU-jxtCDxmUAuXybfTm4bgIgO7Unic/edit#slide=id.gd1ac72da81_0_410 <br>
                <br>
                Please Note:<br>
                <ol>
                <li>The given format is to be followed strictly.</li>
                <li>Skipping any information asked in the presentation may lead to disqualification of that team.</li>
                <li>Deadline for submission of this form is 6th Feb 2022 (Registration Closes Prelem Round ends).</li>
                </ol><br>

                After creation of PPT please submit the form given below:<br>
                https://docs.google.com/forms/d/e/1FAIpQLSc-Vwsr4z0haTHsDyha45fmgvr-pzkE02GCRCgXYAjP9hMVlA/viewform?usp=sf_link
                <br><br>
                Join this WhatsApp Group for regular updates.<br>
                https://chat.whatsapp.com/BWv3VBGviCsHGHMa08TNff<br>
                Regards, <br>
                Team Ideathon2022
            </div>
            '''
        mail.send(msg)
        return ("sent")
    except Exception as e:
        print(e)
        return("Something went wrong")

@app.route('/add-user', methods = ['POST','GET'])
def addUser():
    try :
        teamType=request.form.get('teamType')
        members=request.form.get('members')
        tname=request.form.get('tname')
        tlname = request.form.get('tlname')
        tlemail = request.form.get('tlemail')
        tlphone = request.form.get('tlphone')
        organisation = request.form.get('organization')
        problem_statement = request.form.get('problemStatement')

        if teamType and members and tname and tlname and tlemail and tlphone and organisation and problem_statement:
            parti=participants.query.filter_by(email=tlemail).first()
            if parti:
                te=team.query.filter_by(id=parti.team_id).first()
                if te.problem_statement==problem_statement:
                    return("You have already registered for this problem statement")
            if team.query.filter_by(team_name=tname).first():
                return("Team Name already taken!")
            else:
                db.session.add(team(team_name=tname, team_members=members, team_type=teamType, problem_statement=problem_statement))
                db.session.commit()
                teams=team.query.filter_by(team_name=tname).first()
                db.session.add(participants(name=tlname, email=tlemail, phone=tlphone, organization=organisation, team_name=tname,is_leader=True, team_id=teams.id))
                db.session.commit()
                msg = Message(
                            'Registration Confirmation Team ID '+str(teams.id),
                            sender ='ideathonmriirs1.0@gmail.com',
                            recipients = [tlemail]
                            )
                msg.html = '''Congratulations!! You have successfully registered for Ideathon1.0!<br>
                Our team will contact you shortly!<br>
                Please Note that the Team ID in the subject line is important for the upcoming rounds.
                For any query please feel free to contact us @ ideathonmriirs1.0@gmail.com '''
                mail.send(msg)
                msg = Message(
                            'Registration Confirmation Team ID '+str(teams.id),
                            sender ='ideathonmriirs1.0@gmail.com',
                            recipients = ['ideathonmriirs1.0@gmail.com','sonakshi2500@gmail.com']
                            )
                msg.html = '''<table class="attendees-table" style="text-align:center; width:100vw;">
                <thead>
                    <th>Team_ID</th>
                    <th>Team Name</th>
                    <th>Team Members</th>
                    <th>Team Type</th>
                    <th>Problem Statement</th>
                </thead>
                <tbody>
                        <tr class="view" style="background-color:rgba(162, 87, 187,0.5)">
                            <td>'''+str(teams.id)+'''</td>
                            <td>'''+str(tname)+'''</td>
                            <td>'''+str(members)+'''</td>
                            <td>'''+str(teamType)+'''</td>
                            <td>'''+str(problem_statement)+'''</td>
                        </tr>
                        <tr style="background-color:rgba(254, 101, 195,0.5);">
                            <th>Participant name</th><th>Participant Email</th><th>Participant Phone Number</th><th>Organization</th><th>Is Leader</th>
                        </tr>
                            <tr style="background-color:rgba(254, 101, 195,0.5);">            
                                <td>'''+str(tlname)+'''</td>
                                <td>'''+str(tlemail)+'''</td>
                                <td>'''+str(tlphone)+'''</td>
                                <td>'''+str(organisation)+'''</td>
                                <td>True</td>
                            </tr>
                </tbody>
                </table>'''
                mail.send(msg)
                return ("true")
        else:
            return("Please fill all the fields")
    except Exception as e:
        print(e)
        return("Something went wrong")

@app.route('/add-teamates', methods = ['POST','GET'])
def addteamates():
    try :
        members=int(request.form.get('members'))
        idd=request.form.get('id')
        team_member_name=[]
        team_member_email=[]
        team_member_phone=[]
        for i in range(1,members):
            x=request.form.get('member_name'+str(i))
            y=request.form.get('member_email'+str(i))
            z=request.form.get('member_phone'+str(i))
            team_member_name.append(x)
            team_member_email.append(y)
            team_member_phone.append(z)
        for i in range(len(team_member_name)):
            print(team_member_name)
            if team_member_name[i] and team_member_email[i] and team_member_phone[i]:

                # if participants.query.filter_by(email=team_member_email[i]).first():
                #     return("Email ID already Exists")
                # else:
                    teams=team.query.filter_by(team_name=idd).first()
                    participant=participants.query.filter_by(team_name=idd).first()
                    db.session.add(participants(name=team_member_name[i], email=team_member_email[i], phone=team_member_phone[i], organization=participant.organization, team_name=teams.team_name,is_leader=False, team_id=teams.id))
                    db.session.commit()
                    msg = Message(
                    'Registration Confirmation Team ID '+str(teams.id),
                    sender ='ideathonmriirs1.0@gmail.com',
                    recipients = [team_member_email[i]]
                    )
                    msg.html = '''Congratulations!! You have successfully registered for <b>Ideathon1.0</b>!<br>
                    Our team will contact you shortly!<br>
                    For any query please feel free to contact us @ ideathonmriirs1.0@gmail.com <br>
                    Regards, <br>
                    Team Ideathon1.0<br>
                    '''
                    mail.send(msg)
                    msg = Message(
                            'Registration Confirmation Team ID '+str(teams.id),
                            sender ='ideathonmriirs1.0@gmail.com',
                            recipients = ['ideathonmriirs1.0@gmail.com','sonakshi2500@gmail.com']
                            )
                    msg.html = '''<table class="attendees-table" style="text-align:center; width:100vw;">
                    
                            <tr style="background-color:rgba(254, 101, 195,0.5);">
                                <th>Participant name</th><th>Participant Email</th><th>Participant Phone Number</th><th>Organization</th><th>Is Leader</th>
                            </tr>
                                <tr style="background-color:rgba(254, 101, 195,0.5);">            
                                    <td>'''+str(team_member_name[i])+'''</td>
                                    <td>'''+str(team_member_email[i])+'''</td>
                                    <td>'''+str(team_member_phone[i])+'''</td>
                                    <td>'''+str(participant.organization)+'''</td>
                                    <td>False</td>
                                </tr>
                    </table>'''
                    mail.send(msg)
            else:
                return("Please fill all the fields")
        return ("Thankyou, your registration is confirmed!")
    except Exception as e:
        print(e)
        return("Something went wrong")

@app.route('/attendees')
def attendees():
    teams=team.query.all()
    participant=participants.query.all()
    usr_list = []
    participant_name=[]
    participant_email=[]
    participant_phone=[]
    participant_organization=[]
    participant_is_leader=[]
    for u in teams:
        m=[]
        n=[]
        o=[]
        p=[]
        q=[]
        usr = {
                    'id': u.id,
                    'team_name': u.team_name,
                    'team_members': u.team_members,
                    'team_type': u.team_type,
                    'problem_statement': u.problem_statement,
        }
        usr_list.append(usr)

        for v in participant:
            if u.id==v.team_id:
                m.append(v.name)
                n.append(v.email)
                o.append(v.phone)
                p.append(v.organization)
                q.append(v.is_leader)
        participant_name.append(m)
        participant_email.append(n)
        participant_phone.append(o)
        participant_organization.append(p)
        participant_is_leader.append(q)
    return render_template("attendees.html",users=usr_list, participant_name=participant_name,participant_email=participant_email,participant_phone=participant_phone,participant_organization=participant_organization,participant_is_leader=participant_is_leader)

if __name__ == '__main__':
    app.run(debug=True)