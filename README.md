# Ukraine Connect

#### Video Demo: https://youtu.be/4j9R-02PdsY

#### Description:

# Ukraine Connect

## CS50

> This was my final project for conclude the CS50 Introduction to Computer Sciense course.

> CS, python, flask, flask web framework, web development, CS50

## Features

- [Flask-SocketIO](https://flask-socketio.readthedocs.io/en/latest/)
- [Flask](https://flask.palletsprojects.com/en/1.1.x/)
- [CropperJS](https://fengyuanchen.github.io/cropperjs/)
- [Leaflet](https://leafletjs.com/)

I've used Flask web framework based in Python
its was necessary to use the leaflet library to have the map of ukraine and all the markers of it as the messages,
flask socketio to have broadcast response and cropperJs to use the crop for the profile images.

## Explaining the project

My final project is a website that is a geolocated type of social media, that allow people from Ukraine to connect with each other, sharing their situation and where they are. Being able to like other users messages and post your own with a profile photo and your name within the message.

### Database

The database is ukrainconnect.db, and i used sqlite3 to manage it.

It consists in three tables, users, posts and likes

- Users: user_id (primary key), name, email, hash (password) and photo_filename to store the name of the file

- Posts: user_id (foreign key that references user_id from users), id, text, title, date, lat and long (latitude and longitude of the marker in the map, according to the user local described)

- Likes: just the post_id and user_id to send requests to the database infos

### Storing and displaying posts.

For the posts is required to have the street, city and oblast(region) for checking out the coordinates on mapquestapi.
And if it's valid (at ukraine), it stores the post in database.

```python
if request.method == "POST":

        adress = str(request.form.get("adress"))
        number = str(request.form.get("number"))
        city = str(request.form.get("city"))
        oblast = str(request.form.get("oblast"))
        zipcode = str(request.form.get("zipcode"))
        title = str(request.form.get("title"))
        text = str(request.form.get("text"))

        if not adress or not city or not oblast or not title or not text:
            message = {'text': 'Please, fill all the required fields', 'category': 'warning'}
            return render_template("post.html", message=message, oblasts=get_oblasts(), user=user)

        location = adress + ' ' + number + ' ' + city + ' ' + ' ' + zipcode;

        parameters = {
        "key": "D8vHFz1EnMylphGmYZfxlJPppbJGjfzJ",
        "location": location
        }

        response = requests.get("http://www.mapquestapi.com/geocoding/v1/address", params=parameters).text
        data = json.loads(response)['results'][0]['locations'][0]
        lat = data['latLng']['lat']
        long = data['latLng']['lng']

        if data['adminArea1'] != 'UA':
            message = {'text': 'Please, the adress must be in Ukraine', 'category': 'danger'}
            return render_template("post.html", message=message, oblasts=get_oblasts(), user=user)

        try:
            db.execute('INSERT INTO posts (user_id, text, title, lat, long) VALUES (?, ?, ?, ?, ?)', session['user_id'], text, title, lat, long)
        except:
            message = {'text': 'Something gone wrong', 'category': 'danger'}
            return render_template("post.html", message=message, oblasts=get_oblasts(), user=user)
```

For showing then on the map, the javascript make a request to the server, getting all the posts in JSON.

```javascript
    async _fetchPosts() {
        const params = {
            method: 'POST',
        }
        const response = await fetch('/getPosts', params);
        const posts = await response.json();
        return posts;
        }
```

## Explaining Video

[![EXPLAINING VIDEO](https://img.youtube.com/vi/0xOdWsCU5ko/0.jpg)](https://www.youtube.com/watch?v=0xOdWsCU5ko)

## About CS50

CS50 is a openware course from Havard University and taught by David J. Malan

Introduction to the intellectual enterprises of computer science and the art of programming. This course teaches students how to think algorithmically and solve problems efficiently. Topics include abstraction, algorithms, data structures, encapsulation, resource management, security, and software engineering. Languages include C, Python, and SQL plus students’ choice of: HTML, CSS, and JavaScript (for web development).

Thank you for all CS50.

- Where I get CS50 course?
  https://cs50.harvard.edu/x/2020/

[LinkedIn João Marra](https://www.linkedin.com/in/joaomarr/)
