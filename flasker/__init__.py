from flask import Flask, jsonify, request, abort
import os
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, Plant, setup


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)

    # region Configration
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flasker.sqlite')
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
    # endregion

    def paginate_plants(request, selection):
        plants = [plant.serialize() for plant in selection]
        page = request.args.get('page', 1, type=int)
        plant_per_shelf = 10
        start = (page-1)*plant_per_shelf
        end = start+plant_per_shelf
        return plants[start:end]

    def str_to_bool(s):
        if s == 'True':
            return True
        elif s == 'False':
            return False
        else:
            return None

    setup(app)
    # migrate=Migrate(app,db),db.create_all() instead

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    @app.route('/')
    def hello():
        return jsonify({'message': "Hello World"})

    @app.route('/plants', methods=['GET'])
    def get_plants():
        all_plants = Plant.query.all()
        data = paginate_plants(request, all_plants)
        if len(data) == 0:
            abort(404)
        else:
            return jsonify({'success': True,
                            'plants': data,
                            'total_plants': len(all_plants)})

    @app.route('/plants/<int:plant_id>', methods=['GET'])
    def get_specific_plant(plant_id):
        plant = Plant.query.filter_by(id=plant_id).one_or_none()
        if plant is None:
            abort(404)
        else:
            return jsonify({'success': True,
                            'plant': plant.serialize()})

    @app.route('/plants/<int:plant_id>', methods=['PATCH'])
    def update_plant(plant_id):
        body = request.get_json()
        try:
            plant = Plant.query.filter_by(id=plant_id).one_or_none()
            if plant is None:
                abort(404)
            if 'primary_color' in body:
                plant.primary_color = body.get('primary_color')
            plant.Update()
            return jsonify({'success': True,'id': plant.id})
        except:
            abort(400)

    @app.route('/plants/<int:plant_id>', methods=['DELETE'])
    def delete_plant(plant_id):
        try:
            plant = Plant.query.filter_by(id=plant_id).one_or_none()
            if plant is None:
                abort(404)
            plant.Delete()
            selection = Plant.query.order_by(Plant.id).all()
            current_plants = paginate_plants(request,selection)
            return jsonify({
                'success' : True,
                'deleted': plant.id,
                'plants':current_plants,
                'Total_plants':len(selection)
            })
        except:
            abort(422)

    @app.route('/plants', methods=['POST'])
    def create_plant():
        body = request.get_json()
        new_name= body.get('name',None)
        new_sientific_name=body.get('sientific_name',None)
        new_is_poisonuons=str_to_bool(body.get('is_poisonuons'),None)
        new_primary_color=body.get('primary_color',None)
        try:
            new_plant = Plant(new_name,new_sientific_name,new_is_poisonuons,new_primary_color)
            new_plant.Add()
            selection = Plant.query.all()
            current_plants = paginate_plants(request,selection)
            return jsonify({
                'success':True,
                'created':new_plant.id,
                'plants':current_plants,
                'total plants':len(selection)
            })
        except:
            abort(422)

    @app.route('/smiley')
    def smiley():
        return ':)'

    return app