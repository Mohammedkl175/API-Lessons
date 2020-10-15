import os
import json
import unittest

from flasker import create_app
from models import db,Plant,setup
from flask_sqlalchemy import SQLAlchemy

class PlantTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "planttest"
        self.database_path = "postgresql://{}@{}:{}/{}".format("postgres","localhost","5432",self.database_name)
        setup(self.app,self.database_path)

        self.new_plant = {
            "name": "Watermelon",
            "sientific_name":"Citrullus lanatus",
            "is_poisonuons": False,
            "primary_color":"green"
            }

    def tearDown(self):
        pass

    def test_get_paginait_plants(self):
        res = self.client().get('/plants')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['total_plants'])
        self.assertTrue(len(data['plants']))

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/plants?page=1000',json={'name':'Watermelon'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'Resource Not Found')

    def update_plant_color(self):
        res = self.client().patch('/plant/1',json={'primary_color':'blue'})
        data = json.loads(res.data)
        updated_plant = Plant.query.filter_by(id=1).one_or_none()

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(updated_plant.serialize()['primary_color'],'blue')

    def test_400_faild(self):
        res = self.client().patch('/plants/5')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,400)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'Bad Request')

    def test_delete_plant(self):
        res = self.client().delete('/plants/1')
        data= json.loads(res.data)
        deleted_plant = Plant.query.filter_by(id=1).one_or_none()

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['deleted'],1)
        self.assertTrue(len(data['plants']))
        self.assertTrue(data['Total_plants'])
        self.assertEqual(deleted_plant,None)

    def test_422_if_plant_does_not_exist(self):
        res = self.client().delete('/plants/100')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,422)
        self.assertEqual(data['message'],'unprocessable')
        self.assertEqual(data['success'],False)

    def test_create_plant(self):
        res = self.client().post('/plants',json=self.new_plant)
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertTrue(data['created'])
        self.assertTrue(len(data['plants']))
        self.assertTrue(['total plants'])

    def test_405_if_plant_creation_is_now_allowed(self):
        res = self.client().post('/plants/45',json=self.new_plant)
        data = json.loads(res.data)

        self.assertEqual(res.status_code,405)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'Method Not Allowed')

    def test_search_found_plant(self):
        res = self.client().post('/plants',json={'search':'Carrot'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['total plants'],1)
        self.assertEqual(len(data['plants']),1)

    def test_search_not_found_plant(self):
        res = self.client().post('/plants',json={'search':'Banana'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['total plants'],0)
        self.assertEqual(len(data['plants']),0)

if __name__ == "__main__":
    unittest.main()
    


