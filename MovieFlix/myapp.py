#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 19:04:01 2020

@author: kostis
"""
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from flask import Flask, render_template, flash, request, Markup, session
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import time, os, sys
sys.path.append('./data')
import prepare_data

# Connect to our local MongoDB
mongodb_hostname = os.environ.get("MONGO_HOSTNAME","localhost")
client = MongoClient('mongodb://'+mongodb_hostname+':27017/')

# Choose MovieFlix database
db = client['MovieFlix']
users = db['Users']
movies = db['Movies']


#check if data exist
def check_data():
    try:
        if (movies.find({}).count() == 0) and (users.find({}).count() == 0):
            prepare_data.insert_all_users()
            prepare_data.insert_all_movies()
    except Exception as e:
        print(e)
        raise e
    



# App config.
app = Flask(__name__)
DEBUG = True
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'


class ReusableForm(Form):
    email = TextField('Email:', validators=[validators.DataRequired()])
    password = TextField('Password:', validators=[validators.DataRequired()])
class SignUpForm(Form):
    name = TextField('Name:', validators=[validators.DataRequired()])
    email = TextField('Email:', validators=[validators.DataRequired()])
    password = TextField('Password:', validators=[validators.DataRequired()])
class SearchForm(Form):
    searchterm = TextField('Search term:', validators=[validators.DataRequired()])
class CommentForm(Form):
    email = TextField('Email:', validators=[validators.DataRequired()])
    title = TextField('Title:', validators=[validators.DataRequired()])
    year = TextField('year:', validators=[validators.DataRequired()])
    comment = TextField('comment:', validators=[validators.DataRequired()])
class DeleteCommentForm(Form):
    email = TextField('Email:', validators=[validators.DataRequired()])
    password = TextField('Password:', validators=[validators.DataRequired()])
    title = TextField('Title:', validators=[validators.DataRequired()])
    
    
class NewMovieForm(Form):
    title = TextField('Title:', validators=[validators.DataRequired()])
    year = TextField('Year:', validators=[validators.DataRequired()])
    description = TextField('Description:', validators=[validators.DataRequired()])
    actors = TextField('Actors:', validators=[validators.DataRequired()]) 
    
class DeleteMovieForm(Form):
    title = TextField('Title:', validators=[validators.DataRequired()])
    
class DeleteUserForm(Form):
    email = TextField('Email:', validators=[validators.DataRequired()])
 
    
class DeleteMovieComments(Form):
    title = TextField('Title:', validators=[validators.DataRequired()])
    year = TextField('Year:', validators=[validators.DataRequired()])    



class UpdateMovieTitle(Form):
    title = TextField('Title:', validators=[validators.DataRequired()])
    year = TextField('Year:', validators=[validators.DataRequired()])
    newTitle = TextField('newTitle:', validators=[validators.DataRequired()])
    
    
    
    
class UpdateMovieYear(Form):
    title = TextField('Title:', validators=[validators.DataRequired()])
    year = TextField('Year:', validators=[validators.DataRequired()])
    newYear = TextField('newYear:', validators=[validators.DataRequired()])
    
    
    
    
    
class UpdateMovieDescription(Form):
    title = TextField('Title:', validators=[validators.DataRequired()])
    year = TextField('Year:', validators=[validators.DataRequired()])
    newDescription = TextField('newDescription:', validators=[validators.DataRequired()])
    
    
    
    
    
class UpdateRating(Form):
    title = TextField('Title:', validators=[validators.DataRequired()])
    year = TextField('Year:', validators=[validators.DataRequired()])
    newRating = TextField('newRating:', validators=[validators.DataRequired()])


class AddActor(Form):
    title = TextField('Title:', validators=[validators.DataRequired()])
    year = TextField('Year:', validators=[validators.DataRequired()])
    newActor = TextField('newActor:', validators=[validators.DataRequired()])
    
    
    
class RemoveActor(Form):
    title = TextField('Title:', validators=[validators.DataRequired()])
    year = TextField('Year:', validators=[validators.DataRequired()])
    removeActor = TextField('removeActor:', validators=[validators.DataRequired()])    
    


@app.route("/")
def home_fun():
    session['user']="notloggedin"
    return render_template("home.html")


@app.route("/userhome")
def userhome_fun():
    if session['user'] == "notloggedin":
        flash("Please sign in")
        return render_template("home.html")
    return render_template("userhome.html")
    
@app.route("/signup",methods=['GET', 'POST'])
def signup_fun():
    form = SignUpForm(request.form)
    flash(Markup('To return to home page, please click <a href="/" class="alert-link">here</a>'))
    
    print(form.errors)
    
    if request.method == 'POST':
        name=request.form['name']
        password=request.form['password']
        email=request.form['email']
        print(name," ", email, " ", password)
        existingUser = users.find({'email':email})
        if form.validate():
            if existingUser.count() !=0 :
                flash("There is another user with the same email.")
                
                return render_template("signup.html", form=form)
            else:
                users.insert_one({'name': name, 'email':email, 'password':password, 'comments':[], 'category':'user'})
                flash("You successgully signed up.")
                
                return render_template("signup.html", form=form)

        else:
            flash("All the fields are mandatory!")
            
    return render_template("signup.html")

@app.route('/signin',methods=['GET', 'POST'])
def signin_fun():
    form = ReusableForm(request.form)
    flash(Markup('To return to home page, please click <a href="/" class="alert-link">here</a>'))
    print(form.errors)
    
    if request.method == 'POST':
        password=request.form['password']
        email=request.form['email']
        print( email, " ", password)
        existingUser = users.find({'email':email,'password':password})
        userCategory = users.find({'email':email,'category':'user'})
        adminCategory = users.find({'email':email,'category':'admin'})
        
        if form.validate():
            if existingUser.count() !=0 and userCategory.count()!=0:
                session['user']=email
                flash("You are a simple user!")
                flash(Markup('Successfully logged in, please click <a href="/userhome" class="alert-link">here</a>'))
            elif existingUser.count() !=0 and adminCategory.count()!=0:
                session['user']=email
                flash("You are an admin!")
                flash(Markup('Successfully logged in, please click <a href="/admin" class="alert-link">here</a>'))
            else:
                flash("Please sign up.")
                
                return render_template("signin.html", form=form)

        else:
            flash("All the fields are mandatory!")
        
    
    
    
    
    return render_template("signin.html", form=form)

@app.route('/search',methods=['GET', 'POST'])
def search_fun():
    form = SearchForm(request.form)
    flash(Markup('To return to user home page, please click <a href="/" class="alert-link">here</a>'))
    if session['user'] == "notloggedin":
        flash("Please sign in")
        return render_template("home.html")
    print(form.errors)
    
    if request.method == 'POST':
        searchterm=request.form['searchterm']
        print(searchterm)
        existingMovieTitle = movies.find({'title':searchterm})
        existingMovieYear = movies.find({'year':searchterm})
        existingMovieActor = movies.find({'actors':searchterm})
        myComments = users.find({'email' : searchterm}, {'comments': 1})
        if form.validate():
            if existingMovieTitle.count() !=0 :
                array = list(existingMovieTitle)
                flash(array)
                
                return render_template("moviesearch.html", form=form)
            elif existingMovieYear.count() !=0:
                array = list(existingMovieYear)
                flash(array)
                
                return render_template("moviesearch.html", form=form)
            elif existingMovieActor.count() !=0:
                array = list(existingMovieActor)
                flash(array)
                
                return render_template("moviesearch.html", form=form)
            elif myComments.count() !=0:
                array = list(myComments)
                flash(array)
                
                return render_template("moviesearch.html", form=form)
            else:
                flash("No movie found")
                return render_template("moviesearch.html", form=form)
        else:
            flash("All the fields are mandatory!")
        
    
    
    
    
    return render_template("moviesearch.html", form=form)



@app.route('/comment',methods=['GET', 'POST'])
def comment_fun():
    form = CommentForm(request.form)
    flash(Markup('To return to user home page, please click <a href="/userhome" class="alert-link">here</a>'))
    print(form.errors)
    if session['user'] == "notloggedin":
        flash("Please sign in")
        return render_template("home.html")
    if request.method == 'POST':
        email=request.form['email']
        title=request.form['title']
        year=request.form['year']
        comment=request.form['comment']
        existingMovie = movies.find({'title':title,'year':year})
        existingUser = users.find({'email':email})
        if form.validate():
            if existingMovie.count() !=0 and existingUser.count() !=0:
                movies.update_one({'title': title}, {'$addToSet': {'comments': [{"comment":comment,"email":email}]}})
                users.update_one({'email': email}, {'$addToSet': {'comments': [{"title":title,"comment":comment}]}})
                flash("Your comment was submitted.")
                return render_template("comment.html", form=form)
            
            else:
                flash("Something went terribly wrong.")
                return render_template("comment.html", form=form)
        else:
            flash("All the fields are mandatory!")
        
    
    
    
    
    return render_template("comment.html", form=form)

@app.route('/deletecomment',methods=['GET', 'POST'])
def deletecomment_fun():
    form = DeleteCommentForm(request.form)
    flash(Markup('To return to user home page, please click <a href="/userhome" class="alert-link">here</a>'))
    print(form.errors)
    if session['user'] == "notloggedin":
        flash("Please sign in")
        return render_template("home.html")
    
    if request.method == 'POST':
        email=request.form['email']
        password=request.form['password']
        title=request.form['title']
        existingUser = users.find({'email':email,'password':password})
        if form.validate():
            if existingUser.count() !=0:
                """"movies.update({'title': title}, {'$unset': {'movies': {"email":email}}})"""
                users.update({'email': email}, {'$unset': {'comments': ''}})
                flash("Your comments were deleted from your profile.")
                return render_template("deletecomment.html", form=form)
            
            else:
                flash("Error validating your credentials.")
                return render_template("deletecomment.html", form=form)
        else:
            flash("All the fields are mandatory!")
        
    
    
    
    
    return render_template("deletecomment.html", form=form)


@app.route('/deleteaccount',methods=['GET', 'POST'])
def deleteaccount_fun():
    form = ReusableForm(request.form)
    flash(Markup('To return to user home page, please click <a href="/userhome" class="alert-link">here</a>'))
    print(form.errors)
    
    if session['user'] == "notloggedin":
        flash("Please sign in")
        return render_template("home.html")
    
    if request.method == 'POST':
        email=request.form['email']
        password=request.form['password']
        existingUser = users.find({'email':email,'password':password})
        if form.validate():
            if existingUser.count() !=0:
                users.delete_one({'email': email})
                flash("Your account was successfully deleted.")
                flash(Markup('To return to MovieFlix home page, please click <a href="/" class="alert-link">here</a>'))
                return render_template("deleteaccount.html", form=form)
            
            else:
                flash("Error validating your credentials.")
                return render_template("deleteaccount.html", form=form)
        else:
            flash("All the fields are mandatory!")
        
    
    
    
    
    return render_template("deleteaccount.html", form=form)

@app.route("/admin")
def admin_fun():
    if session['user'] == "notloggedin":
        flash("Please sign in")
        return render_template("home.html")
    flash(Markup('To return to MovieFlix home page, please click <a href="/" class="alert-link">here</a>'))
    return render_template("admin.html")




@app.route('/newmovie',methods=['GET', 'POST'])
def newmovie_fun():
    form = NewMovieForm(request.form)
    flash(Markup('To return to admin home page, please click <a href="/admin" class="alert-link">here</a>'))
    print(form.errors)
    
    if session['user'] == "notloggedin":
        flash("Please sign in")
        return render_template("home.html")
    
    if request.method == 'POST':
        title=request.form['title']
        description=request.form['description']
        actors=request.form['actors']
        year=request.form['year']
        
        if form.validate():
            movies.insert_one({'title': title, 'description':description, 'year':year, 'actors':actors, 'rating':'', 'comments':[]})
                
            flash("The movie was added to the database.")
        else:
            flash("All the fields are mandatory!")
        
    
    
    
    
    return render_template("newmovie.html", form=form)



@app.route('/deletemovie',methods=['GET', 'POST'])
def deletemovie_fun():
    form = DeleteMovieForm(request.form)
    flash(Markup('To return to admin home page, please click <a href="/admin" class="alert-link">here</a>'))
    print(form.errors)
    
    if session['user'] == "notloggedin":
        flash("Please sign in")
        return render_template("home.html")
    
    if request.method == 'POST':
        title=request.form['title']
        existingMovie = movies.find({'title':title})
        if form.validate():
            if existingMovie.count() !=0:
                movies.delete_one({'title': title})
                flash("The movie was successfully deleted.")
                flash(Markup('To return to admin home page, please click <a href="/admin" class="alert-link">here</a>'))
                return render_template("deletemovie.html", form=form)
            
            else:
                flash("There is no such movie in the database.")
                return render_template("deletemovie.html", form=form)
        else:
            flash("All the fields are mandatory!")
        
    
    
    
    
    return render_template("deletemovie.html", form=form)



@app.route('/deleteuser',methods=['GET', 'POST'])
def deleteuser_fun():
    form = DeleteUserForm(request.form)
    flash(Markup('To return to admin home page, please click <a href="/admin" class="alert-link">here</a>'))
    
    if session['user'] == "notloggedin":
        flash("Please sign in")
        return render_template("home.html")
    
    if request.method == 'POST':
        email=request.form['email']
        existingUser = users.find({'email':email , 'category':'user'})
        if form.validate():
            if existingUser.count() !=0:
                users.delete_one({'email': email})
                flash("This user was successfully deleted.")
                return render_template("deleteuser.html", form=form)
            
            else:
                flash("There is no such user in the database.")
                return render_template("deleteuser.html", form=form)
        else:
            flash("All the fields are mandatory!")
        
    
    
    
    
    return render_template("deleteuser.html", form=form)




@app.route('/changecategory',methods=['GET', 'POST'])
def changecategory_fun():
    form = DeleteUserForm(request.form)
    flash(Markup('To return to admin home page, please click <a href="/admin" class="alert-link">here</a>'))
    
    if session['user'] == "notloggedin":
        flash("Please sign in")
        return render_template("home.html")
    
    if request.method == 'POST':
        email=request.form['email']
        existingUser = users.find({'email':email , 'category':'user'})
        myquery = { "email": email }
        newvalues = { "$set": { "category": "admin" } }
        if form.validate():
            if existingUser.count() !=0:
                users.update_one(myquery, newvalues)
                flash("This user was successfully promoted to admin.")
                return render_template("changecategory.html", form=form)
            
            else:
                flash("There is no such user in the database.")
                return render_template("changecategory.html", form=form)
        else:
            flash("All the fields are mandatory!")
        
    
    
    
    
    return render_template("changecategory.html", form=form)




@app.route('/deletemoviecomments',methods=['GET', 'POST'])
def deletemoviecomments_fun():
    form = DeleteMovieComments(request.form)
    flash(Markup('To return to admin home page, please click <a href="/admin" class="alert-link">here</a>'))
    
    if session['user'] == "notloggedin":
        flash("Please sign in")
        return render_template("home.html")
    
    if request.method == 'POST':
        title=request.form['title']
        year=request.form['year']
        existingMovie = movies.find({'title':title , 'year':year})
        if form.validate():
            if existingMovie.count() !=0:
                movies.update({'title': title,'year':year}, {'$unset': {'comments': ''}})
                flash("The comments for this movie were successfully removed.")
                return render_template("deletemoviecomments.html", form=form)
            
            else:
                flash("There is no such movie in the database.")
                return render_template("deletemoviecomments.html", form=form)
        else:
            flash("All the fields are mandatory!")
        
    
    
    
    
    return render_template("deletemoviecomments.html", form=form)


@app.route('/updatemovietitle',methods=['GET', 'POST'])
def updatemovietitle_fun():
    form = UpdateMovieTitle(request.form)
    flash(Markup('To return to admin home page, please click <a href="/admin" class="alert-link">here</a>'))
    
    if session['user'] == "notloggedin":
        flash("Please sign in")
        return render_template("home.html")
    
    if request.method == 'POST':
        title=request.form['title']
        year=request.form['year']
        newTitle=request.form['newTitle']
        existingMovie = movies.find({'title':title , 'year':year})
        myquery = { "title": title, "year":year }
        newvalues = { "$set": { "title": newTitle } }
        if form.validate():
            if existingMovie.count() !=0:
                movies.update_one(myquery, newvalues)
                flash("This movie title was successfully updated.")
                return render_template("updatemovietitle.html", form=form)
            
            else:
                flash("There is no such movie in the database.")
                return render_template("updatemovietitle.html", form=form)
        else:
            flash("All the fields are mandatory!")
        
    
    
    
    
    return render_template("updatemovietitle.html", form=form)


@app.route('/updatemovieyear',methods=['GET', 'POST'])
def updatemovieyear_fun():
    form = UpdateMovieYear(request.form)
    flash(Markup('To return to admin home page, please click <a href="/admin" class="alert-link">here</a>'))
    if session['user'] == "notloggedin":
        flash("Please sign in")
        return render_template("home.html")
    
    if request.method == 'POST':
        title=request.form['title']
        year=request.form['year']
        newYear=request.form['newYear']
        existingMovie = movies.find({'title':title , 'year':year})
        myquery = { "title": title, "year":year }
        newvalues = { "$set": { "year": newYear} }
        if form.validate():
            if existingMovie.count() !=0:
                movies.update_one(myquery, newvalues)
                flash("This movie year was successfully updated.")
                return render_template("updatemovieyear.html", form=form)
            
            else:
                flash("There is no such movie in the database.")
                return render_template("updatemovieyear.html", form=form)
        else:
            flash("All the fields are mandatory!")
        
    
    
    
    
    return render_template("updatemovieyear.html", form=form)





@app.route('/updatemovieplot',methods=['GET', 'POST'])
def updatemoviedescription_fun():
    form = UpdateMovieDescription(request.form)
    flash(Markup('To return to admin home page, please click <a href="/admin" class="alert-link">here</a>'))
    
    if session['user'] == "notloggedin":
        flash("Please sign in")
        return render_template("home.html")
    
    if request.method == 'POST':
        title=request.form['title']
        year=request.form['year']
        newDescription=request.form['newDescription']
        existingMovie = movies.find({'title':title , 'year':year})
        myquery = { "title": title, "year":year }
        newvalues = { "$set": { "description": newDescription} }
        if form.validate():
            if existingMovie.count() !=0:
                movies.update_one(myquery, newvalues)
                flash("This movie description was successfully updated.")
                return render_template("updatemoviedescription.html", form=form)
            
            else:
                flash("There is no such movie in the database.")
                return render_template("updatemoviedescription.html", form=form)
        else:
            flash("All the fields are mandatory!")
        
    
    
    
    
    return render_template("updatemoviedescription.html", form=form)






@app.route('/updaterating',methods=['GET', 'POST'])
def updaterating_fun():
    form = UpdateRating(request.form)
    flash(Markup('To return to admin home page, please click <a href="/admin" class="alert-link">here</a>'))
    
    if session['user'] == "notloggedin":
        flash("Please sign in")
        return render_template("home.html")
    
    if request.method == 'POST':
        title=request.form['title']
        year=request.form['year']
        newRating=request.form['newRating']
        existingMovie = movies.find({'title':title , 'year':year})
        myquery = { "title": title, "year":year }
        newvalues = { "$set": { "rating": newRating} }
        if form.validate():
            if existingMovie.count() !=0:
                movies.update_one(myquery, newvalues)
                flash("This movie rating was successfully updated.")
                return render_template("updaterating.html", form=form)
            
            else:
                flash("There is no such movie in the database.")
                return render_template("updaterating.html", form=form)
        else:
            flash("All the fields are mandatory!")
        
    
    
    
    
    return render_template("updaterating.html", form=form)


@app.route('/addactor',methods=['GET', 'POST'])
def addactor_fun():
    form = AddActor(request.form)
    flash(Markup('To return to admin home page, please click <a href="/admin" class="alert-link">here</a>'))
    
    if session['user'] == "notloggedin":
        flash("Please sign in")
        return render_template("home.html")
    
    if request.method == 'POST':
        title=request.form['title']
        year=request.form['year']
        newActor=request.form['newActor']
        existingMovie = movies.find({'title':title , 'year':year})
        myquery = { "title": title, "year":year }
        newvalues = { "$addToSet": { "actors": newActor} }
        if form.validate():
            if existingMovie.count() !=0:
                movies.update_one(myquery, newvalues)
                flash("This actor was successfully added.")
                return render_template("addactor.html", form=form)
            
            else:
                flash("There is no such movie in the database.")
                return render_template("addactor.html", form=form)
        else:
            flash("All the fields are mandatory!")
        
    
    
    
    
    return render_template("addactor.html", form=form)






@app.route('/removeactor',methods=['GET', 'POST'])
def removeactor_fun():
    form = RemoveActor(request.form)
    flash(Markup('To return to admin home page, please click <a href="/admin" class="alert-link">here</a>'))
    
    if session['user'] == "notloggedin":
        flash("Please sign in")
        return render_template("home.html")
    
    if request.method == 'POST':
        title=request.form['title']
        year=request.form['year']
        removeActor=request.form['removeActor']
        existingMovie = movies.find({'title':title , 'year':year})
        myquery = { "title": title, "year":year }
        newvalues = { "$pull": { "actors": removeActor} }
        if form.validate():
            if existingMovie.count() !=0:
                movies.update_one(myquery, newvalues)
                flash("This actor was successfully removed.")
                return render_template("removeactor.html", form=form)
            
            else:
                flash("There is no such movie in the database.")
                return render_template("removeactor.html", form=form)
        else:
            flash("All the fields are mandatory!")
        
    
    
    
    
    return render_template("removeactor.html", form=form)



    
if __name__ == "__main__":
    check_data()
    app.run(debug=True, host='0.0.0.0', port=5000)

