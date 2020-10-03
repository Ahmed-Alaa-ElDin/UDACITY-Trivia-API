import os
import unittest
from flask import Flask, request, abort, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from flask_migrate import Migrate
from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    template_dir = os.path.abspath('../../frontend/src')
    app = Flask(__name__, template_folder=template_dir)
    setup_db(app)
    migrate = Migrate(app, db)

    '''
    Set up CORS
    '''
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers', 'Content-Type, Authorization'
            )
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET, PUT, POST, PATCH, DELETE, OPTIONS'
            )
        return response

    '''
    All available categories.
    '''
    @app.route("/categories")
    def get_categories():
        categories_query = Category.query.all()

        if len(categories_query) > 0:
            result = {}
            for category_query in categories_query:
                result[category_query.id] = category_query.type
            return jsonify({'categories': result})
        else:
            abort(400)

    '''
    List of Pag. Questions
    '''
    @app.route("/questions")
    def get_pag_questions():
        items_limit = request.args.get('limit', QUESTIONS_PER_PAGE, type=int)
        page = request.args.get("pages", 1, type=int)
        current_index = page - 1
        ques_result = []
        questions_query = Question.query.order_by(
                Question.id
            ).limit(items_limit).offset(current_index * items_limit).all()
        formatted_questions = [
            question_query.format() for question_query in questions_query
            ]
        categories_query = Category.query.all()
        cat_result = {}
        for category_query in categories_query:
            cat_result[category_query.id] = category_query.type
        if len(formatted_questions[start_page:end_page]) != 0:
            result = {
                "questions": formatted_questions,
                "total_questions": len(questions_query),
                "current_category": "",
                "categories": cat_result
            }
            return jsonify(result)
        else:
            abort(404)

    '''
    Delete a Question
    '''
    @app.route("/questions/<int:id>", methods=["DELETE"])
    def delete_question(id):
        error = False
        try:
            delete_ques = Question.query.filter(Question.id == id).first()
            db.session.delete(delete_ques)
            db.session.commit()
            questions_query = Question.query.all()
            formatted_questions = [
                question_query.format() for question_query in questions_query
                ]
            return jsonify({"questions": formatted_questions})
        except Exception:
            error = True
            db.session.rollback()
        finally:
            db.session.close()
        if error:
            abort(404)

    '''
    Add a New Question
    '''
    @app.route("/questions", methods=["POST"])
    def add_question():
        error = False
        try:
            res = request.get_json()
            new_question = Question(
                question=res["question"], answer=res["answer"],
                category=res["category"], difficulty=res["difficulty"]
                )
            db.session.add(new_question)
            db.session.commit()
            return jsonify(res["question"])
        except Exception:
            error = True
            db.session.rollback()
        finally:
            db.session.close()
        if error:
            abort(422)
    '''
    Search a Question
    '''

    @app.route("/questions/search", methods=["POST"])
    def search_ques():
        term = request.get_json()["searchTerm"]
        page = 1
        start_page = (page - 1) * QUESTIONS_PER_PAGE
        end_page = start_page + QUESTIONS_PER_PAGE
        ques_result = []
        questions_query_search = Question.query.filter(
            Question.question.ilike('%' + term + '%')
            ).all()
        formatted_questions = [
            question_query.format() for question_query
            in questions_query_search
            ]
        categories_query = Category.query.all()
        cat_result = {}
        for category_query in categories_query:
            cat_result[category_query.id] = category_query.type
        result = {
            "questions": formatted_questions[start_page:end_page],
            "total_questions": len(questions_query_search),
            "current_category": "",
            "categories": cat_result
        }
        return jsonify(result)
    '''
    Display Question According to Category
    '''
    @app.route("/categories/<int:id>/questions")
    def get_cat_questions(id):
        items_limit = request.args.get('limit', QUESTIONS_PER_PAGE, type=int)
        page = request.args.get("pages", 1, type=int)
        current_index = page - 1
        ques_result = []
        try:
            questions_query = Question.query.filter(
                Question.category == str(id)
                ).order_by(
                    Question.id
                ).limit(items_limit).offset(current_index * items_limit).all()
            formatted_questions = [
                question_query.format() for question_query in questions_query
                ]
            categories_query_all = Category.query.all()
            categories_query_selected = Category.query.filter(
                Category.id == id
                ).first()
            cat_result = {}
            for category_query in categories_query_all:
                cat_result[category_query.id] = category_query.type
            result = {
                "questions": formatted_questions[start_page:end_page],
                "total_questions": len(questions_query),
                "current_category": categories_query_selected.type,
                "categories": cat_result
            }
            return jsonify(result)
        except Exception:
            abort(404)
    '''
    Get a Question for Quiz
    '''
    @app.route("/quizzes", methods=["POST"])
    def quizizz():
        request_quiz = request.get_json()
        prev_ques_ind = request_quiz["previous_questions"]
        quiz_cat = request_quiz["quiz_category"]["id"]

        if quiz_cat != 0:
            categories_query_all = Category.query.filter(
                Category.id == quiz_cat
                ).all()
            if categories_query_all == []:
                abort(404)

            questions_query = Question.query.filter(
                Question.category == str(quiz_cat)
                ).all()
        else:
            questions_query = Question.query.all()

        all_ques_ind = [
            question_query.id for question_query in questions_query
            ]
        new_ques_ind = list(set(all_ques_ind) - set(prev_ques_ind))
        if new_ques_ind == []:
            question = ""
        else:
            current_question = random.choice(new_ques_ind)
            get_current_question = Question.query.filter(
                Question.id == int(current_question)
                ).first()
            question = {
                "id": get_current_question.id,
                "question": get_current_question.question,
                "answer": get_current_question.answer
            }

        return jsonify({"question": question})

    '''
    Error Handler
    '''

    @app.errorhandler(400)
    def question_not_found(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "No Categories Has Been Found"
        }), 400

    @app.errorhandler(404)
    def question_not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "This Question Not Found"
        }), 404

    @app.errorhandler(422)
    def question_not_found(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Can't Process Your Data"
        }), 422

    @app.errorhandler(500)
    def question_not_found(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "There is an Error in Server"
        }), 500

    return app
