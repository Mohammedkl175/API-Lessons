from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def setup(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@localhost:5432/plant'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app=app
    db.init_app(app)
    db.create_all()

class Plant(db.Model):
    __tablename__='plants'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String())
    sientific_name = db.Column(db.String())
    is_poisonuons = db.Column(db.Boolean())
    primary_color = db.Column(db.String())

    def _init_(name,sientific_name,is_poisonuons,primary_color):
        self.name = name
        self.sientific_name = sientific_name
        self.is_poisonuons = is_poisonuons
        self.primary_color = primary_color

    def serialize(self):
        return {
            "id" : self.id,
            "name": self.name,
            "sientific_name":self.sientific_name,
            "is_poisonuons":self.is_poisonuons,
            "primary_color":self.primary_color
        }

    def Add(self):
        db.session.add(self)
        db.session.commit()
    def Update(self):
        db.session.commit()
    def Delete(self):
        db.session.delete(self)
        db.session.commit()
