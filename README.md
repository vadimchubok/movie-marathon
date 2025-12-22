Movie Marathon
Movie Marathon is a web application for browsing and rating movies. Users can create accounts, view
movies, leave ratings, and write comments.
Features
• User registration and login
• Browse movie list and detailed information
• Rate movies
• Add comments and reviews
• Schedule and organize movie nights

How to Run
1. Fork the repository on GitHub
2. Clone your forked repository
git clone your-forked-repo-link
1. Open the project folder in your IDE
2. Open a terminal in the project folder
3. Create a branch for your work and switch to it
git checkout -b develop
1. If your IDE did not automatically create a virtual environment:
python -m venv venv
venv\Scripts\activate # on Windows
source venv/bin/activate # on macOS/Linux
pip install -r requirements.txt
1. Run the project:
python manage.py runserver
Test Users
Username Password
testuser1 TestPass123
testuser2 TestPass123
Структура проекту
![Movie Detail](assets/MainStrucutre.png)