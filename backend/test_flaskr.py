import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_host = os.getenv('DB_HOST', '127.0.0.1:5432')
        self.database_user = os.getenv('DB_USER', 'postgres')
        self.database_password = os.getenv('DB_PASSWORD', 'postgres')
        self.database_name = os.getenv('DB_NAME', 'trivia_test')


        database_path = 'postgresql://{}:{}@{}/{}'.format(
            self.database_user, self.database_password,
            self.database_host, self.database_name
            )
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            DB_USER, self.database_password, DB_HOST, self.database_name
        )
        setup_db(self.app, self.database_path)

        self.new_question = {
            "question": "How Are You ?",
            "answer": "Fine",
            "category": "2",
            "difficulty": 1
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for
    expected errors.
    """
    def test_get_categories_success(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["categories"])

    def test_get_questions_success(self):
        res = self.client().get('/questions?pages=1')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["questions"])

    def test_get_questions_fail(self):
        res = self.client().get('/questions?pages=100')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)

    def test_add_new_question_right(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertMultiLineEqual(data, self.new_question['question'])

    def test_add_new_question_error(self):
        res = self.client().post('/questions', json={
            "cat": "How Are You ?"
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)

    def test_delete_ques_right(self):
        delete_id = Question.query.first()
        res = self.client().delete('/questions/' + str(delete_id.id))
        data = json.loads(res.data)
        question = Question.query.filter(Question.id == 1).first()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(question, None)

    def test_delete_ques_error(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)
        question = Question.query.filter(Question.id == 1000).first()
        self.assertEqual(res.status_code, 404)
        self.assertEqual(question, None)

    def test_search_success(self):
        res = self.client().post('/questions/search', json={
            "searchTerm": "title"
            })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)

    def test_search_fail(self):
        res = self.client().post('/questions/search', json={
            "searchTerm": "man"
            })
        data = json.loads(res.data)

    def test_question_by_category_success(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)

    def test_question_by_category_fail(self):
        res = self.client().get('/categories/10/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)

    def test_get_random_question_success(self):
        res = self.client().post('/quizzes', json={
            "previous_questions": [],
            "quiz_category": {"id": 2, "type": "art"}})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["question"]["id"])

    def test_get_random_question_fail(self):
        res = self.client().post(
            '/quizzes', json={
                "previous_questions": [],
                "quiz_category": {"id": 8, "type": "art"}
                }
            )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
