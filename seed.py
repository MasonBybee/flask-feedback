from app import db, User, Feedback
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()


def seed_database():
    user1 = User.register(
        username="user1",
        password="password1",
        email="user1@example.com",
        first_name="John",
        last_name="Doe",
    )

    user2 = User.register(
        username="user2",
        password="password2",
        email="user2@example.com",
        first_name="Jane",
        last_name="Smith",
    )

    feedback1 = Feedback(title="Feedback 1", content="This is feedback 1", user=user1)
    feedback2 = Feedback(title="Feedback 2", content="This is feedback 2", user=user1)
    feedback3 = Feedback(title="Feedback 3", content="This is feedback 3", user=user2)

    db.session.add_all([user1, user2, feedback1, feedback2, feedback3])
    db.session.commit()


if __name__ == "__main__":
    from app import app

    with app.app_context():
        db.create_all()
        seed_database()
