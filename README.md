# Job Application Tracker

## Project Description

The Job Application Tracker is a full-stack web application
developed using Python, Flask, MySQL, HTML, CSS, and Bootstrap.

The application allows users to organize companies, job listings,
job applications, and professional contacts.

It also includes a Job Match feature that compares a user's skills
with job requirements and calculates a matching percentage.

## Technologies Used

- Python 3
- Flask
- MySQL
- MySQL Connector
- HTML5
- CSS3
- Bootstrap 5
- Git and GitHub

## Features

### Dashboard
Displays statistics for companies, jobs, applications, and contacts.

### Companies
Allows users to add, view, edit, and delete companies.

### Jobs
Allows users to manage job listings, salary information,
job types, and required skills.

### Applications
Tracks application dates, application status, resume versions,
cover letters, and interview information.

### Contacts
Stores recruiter and professional contact information.

### Job Match
Compares user-entered skills with job requirements and calculates
a matching percentage.

## Database Design

The MySQL database is named job_tracker.

It contains four tables:

1. companies
2. jobs
3. applications
4. contacts

The database uses primary keys, foreign keys, ENUM fields,
and JSON columns.

## Installation Instructions

### 1. Clone the Repository

git clone YOUR_GITHUB_REPOSITORY_URL

### 2. Enter the Project Folder

cd job_tracker

### 3. Install Dependencies

pip install -r requirements.txt

### 4. Create the Database

Open MySQL Workbench and execute the schema.sql file.

### 5. Configure Database Connection

Open database.py and enter your local MySQL username
and password.

### 6. Run the Application

python app.py

### 7. Open the Website

http://127.0.0.1:5000

## Job Matching Calculation

The application calculates the percentage of required job skills
that match the user's entered skills.

Match Percentage = (Matched Skills / Required Skills) * 100

## AI Documentation

See AI_USAGE.md for documentation of AI tools,
prompts, modifications, and lessons learned.

## Developer

Student Name: Liam Manzanilla

Course: COP4751

Project: Job Application Tracker
