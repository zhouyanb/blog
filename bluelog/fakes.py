import random
from faker import Faker
from sqlalchemy.exc import IntegrityError
from bluelog.extensions import db
from bluelog.models import Admin,Comment,Category,Post


def fake_admin():
    admin=Admin(
        username='admin',
        blog_title='blog',
        blog_sub_title="This is a fake blog",
        name='zyb',
        about='A fake admin.Made by zyb,just for the homework.'
    )
    admin.set_password('helloflask')
    db.session.add(admin)
    db.session.commit()

fake=Faker()
def fake_categories(count=10):
    category=Category(name='Default')
    db.session.add(category)
    for i in range(count):
        category=Category(name=fake.word())
        db.session.add(category)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

def fake_posts(count=50):
    for i in range(count):
        post=Post(
            title=fake.sentence(),
            body=fake.text(2000),
            category=Category.query.get(random.randint(1,Category.query.count())),
            timestamp=fake.date_time_this_year()
        )
        db.session.add(post)
    db.session.commit()

def fake_comments(count=500):
    for i in range(count):
        comment=Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=True,
            post=Post.query.get(random.randint(1,Post.query.count()))
        )
        db.session.add(comment)
    salt=int(count*0.1)
    for i in range(salt):
        comment=Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=False,
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)
    for i in range(salt):
        comment=Comment(
            author='zyb',
            email='jsuzyb@163.com',
            site='https://mail.163.com/',
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            from_admin=True,
            reviewed=True,
            post=Post.query.get(random.randint(1,Post.query.count()))
        )
        db.session.add(comment)
    db.session.commit()
    for i in range(salt):
        comment=Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=True,
            replied=Comment.query.get(random.randint(1,Comment.query.count())),
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)
    db.session.commit()
