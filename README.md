# Attendance-System-using-Facial-Recognition

     The Goal of this project is to maintain the attendance of the students using facial recognition.
     
# Motivation
     
     The Traditional way of maintaining the attendance using books is time consuming.
     This project helps to overcome this disadvantage by using Machine learning concepts to recognize students faces.
     
# Tech/framework used

This project is implemented using pycharm ide and flask framework.
      
Google Calendar api is used to retrieve the events of the subjects at a particular time.

[face-recognition](https://github.com/ageitgey/face_recognition)  is the world's simplest face recognition library used to recognize and manipulate faces.
Built using dlib's state-of-the-art face recognition built with deep learning.
The model has an accuracy of 99.38% on the Labeled Faces in the Wild benchmark.

# Installation
#### Requirements
 * Python 3.3+ or Python 2.7
 * macOS or Linux (Windows not officially supported, but might work)
#### Installation steps
First, make sure you have dlib already installed with Python bindings:
* [How to install dlib from source on macOS or Ubuntu](https://gist.github.com/ageitgey/629d75c1baac34dfa5ca2a1928a7aeaf)

Now, install all the packages in requirements.txt

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;```pip3 install -r requirements.txt```

# Deployment

This project is hosted using heroku at [location](https://mark-my-attendance-6666.herokuapp.com/).
