import os
import click
from flask import *
import logging
from flask_login import current_user
from flask_wtf.csrf import CSRFError

from bluelog.blueprints.admin import admin_bp
from bluelog.blueprints.auth import auth_bp
from bluelog.settings import config
from bluelog.blueprints.blog import blog_bp
from bluelog.extensions import *
from bluelog.models import *

def create_app(config_name=None):
    if config_name is None:
        config_name=os.getenv('FLASK_CONFIG','development')
    app=Flask('bluelog')
    app.config.from_object(config[config_name])
    register_logging(app)
    register_extensions(app)
    register_blueprints(app)
    register_commands(app)
    app.register_blueprint(blog_bp)
    register_errors(app)
    register_template_context(app)
    register_request_handlers(app)
    return app

def register_logging(app):
    pass

def register_extensions(app):
    bootstrap.init_app(app)
    db.init_app(app)
    ckeditor.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

def register_blueprints(app):
    app.register_blueprint(blog_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(auth_bp, url_prefix='/auth')

def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db,Admin=Admin,Post=Post,Category=Category,Comment=Comment)

def register_template_context(app):
    @app.context_processor
    def make_template_context():
        admin = Admin.query.first()
        categories = Category.query.order_by(Category.name).all()
        links = Link.query.order_by(Link.name).all()
        if current_user.is_authenticated:
            unread_comments = Comment.query.filter_by(reviewed=False).count()
        else:
            unread_comments = None
        return dict(
            admin=admin,categories=categories,
            links=links,unread_comments=unread_comments)

def register_errors(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'),400
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('errors/400.html', description=e.description), 400

def register_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def initdb(drop):
        """Initialize the database."""
        if drop:
            click.confirm('This operation will delete the database, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Drop tables.')
        db.create_all()
        click.echo('Initialized database.')

    @app.cli.command()
    @click.option('--category',default=10,help='fake categories,default is 10')
    @click.option('--post',default=50,help='fake posts,default is 50')
    @click.option('--comment',default=500,help='fake comments,default is 500')
    def forge(category,post,comment):
        """Create fake categories , posts and comments"""
        from bluelog.fakes import fake_categories,fake_comments,fake_admin,fake_posts
        db.drop_all()
        db.create_all()
        click.echo('create fake admin')
        fake_admin()
        click.echo('create %d fake categories'%category)
        fake_categories()
        click.echo('create %d fake posts'%post)
        fake_posts()
        click.echo('create %d fake comments'%comment)
        fake_comments()
        click.echo('done')

    @app.cli.command()
    @click.option('--username',prompt=True,help='The username used to login')
    @click.option('--password',prompt=True,hide_input=True,confirmation_prompt=True,help='The password used to login')
    def init(username,password):
        """Init bluelog"""
        click.echo('Initialize the blog')
        db.create_all()
        admin=Admin.query.first()
        if admin:
            click.echo('The admin already exit,updating...')
            admin.username=username
            admin.set_password(password)
        else:
            click.echo('Creating the admin...')
            admin=Admin(
                username=username,
                blog_title='Bluelog',
                blog_sub_title='This is a fake blog',
                name='Admin',
                about='Anything about you.0'
            )
            admin.set_password(password)
            db.session.add(admin)
        category=Category.query.first()
        if category is None:
            click.echo('Creating the default category...')
            category=Category(name='Default')
            db.session.add(category)
        db.session.commit()
        click.echo('done')



def register_request_handlers(app):
    pass




