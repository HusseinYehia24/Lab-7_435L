import runpy
from pathlib import Path

import pytest
from flask import json

import app as user_app


@pytest.fixture
def database(tmp_path, monkeypatch):
    """Create a separate empty database for each database/API test."""
    monkeypatch.chdir(tmp_path)
    user_app.create_db_table()


@pytest.fixture
def user():
    """The example user from the Lab 5 manual."""
    return {
        'name': 'John Doe',
        'email': 'jondoe@gamil.com',
        'phone': '067765434567',
        'address': 'John Doe Street, Innsbruck',
        'country': 'Austria',
    }


def test_database_created_with_initial_users(tmp_path, monkeypatch):
    app_path = Path(user_app.__file__).resolve()
    monkeypatch.chdir(tmp_path)

    # Run normal startup without starting a web server.
    monkeypatch.setattr(user_app.Flask, 'run', lambda self: None)

    assert not Path('database.db').exists()

    runpy.run_path(str(app_path), run_name='__main__')

    expected = [
        {
            'user_id': 1,
            'name': 'Hussein Yehia',
            'email': 'hussein.yehia@example.com',
            'phone': '0000000001',
            'address': 'Example Address 1',
            'country': 'Lebanon',
        },
        {
            'user_id': 2,
            'name': 'Ali Khasse',
            'email': 'ali.khasse@example.com',
            'phone': '0000000002',
            'address': 'Example Address 2',
            'country': 'Lebanon',
        },
        {
            'user_id': 3,
            'name': 'Farid Saker',
            'email': 'farid.saker@example.com',
            'phone': '0000000003',
            'address': 'Example Address 3',
            'country': 'Lebanon',
        },
        {
            'user_id': 4,
            'name': 'Moosa Koosa',
            'email': 'moosa.koosa@example.com',
            'phone': '0000000004',
            'address': 'Example Address 4',
            'country': 'Lebanon',
        },
        {
            'user_id': 5,
            'name': 'Talal Balal',
            'email': 'talal.balal@example.com',
            'phone': '0000000005',
            'address': 'Example Address 5',
            'country': 'Lebanon',
        },
    ]

    assert Path('database.db').is_file()
    assert user_app.get_users() == expected

    # A second startup must not duplicate the initial users.
    runpy.run_path(str(app_path), run_name='__main__')
    assert user_app.get_users() == expected


def test_insert_user(database, user):
    inserted_user = user_app.insert_user(user)
    expected = {'user_id': 1, **user}

    assert inserted_user == expected
    assert user_app.get_user_by_id(1) == expected


def test_get_users(database, user):
    user_app.insert_user(user)

    assert user_app.get_users() == [{'user_id': 1, **user}]


def test_get_user_by_id(database, user):
    user_app.insert_user(user)

    assert user_app.get_user_by_id(1) == {'user_id': 1, **user}


def test_update_user(database, user):
    user_app.insert_user(user)
    updated_user = {
        'user_id': 1,
        **user,
        'name': 'John Doe Updated',
    }

    assert user_app.update_user(updated_user) == updated_user
    assert user_app.get_user_by_id(1) == updated_user


def test_delete_user(database, user):
    user_app.insert_user(user)

    assert user_app.delete_user(1) == {
        'status': 'User deleted successfully'
    }
    assert user_app.get_user_by_id(1) == {}
    assert user_app.get_users() == []


def test_api_get_user(database, user):
    user_app.insert_user(user)

    response = user_app.app.test_client().get('/api/users/1')
    data = json.loads(response.get_data(as_text=True))

    assert response.status_code == 200
    assert data == {'user_id': 1, **user}


def test_api_add_user(database, user):
    response = user_app.app.test_client().post(
        '/api/users/add',
        data=json.dumps(user),
        content_type='application/json',
    )

    data = json.loads(response.get_data(as_text=True))
    expected = {'user_id': 1, **user}

    assert response.status_code == 200
    assert data == expected
    assert user_app.get_user_by_id(1) == expected


def test_api_update_user(database, user):
    user_app.insert_user(user)
    updated_user = {
        'user_id': 1,
        **user,
        'name': 'John Doe Updated',
    }

    response = user_app.app.test_client().put(
        '/api/users/update',
        data=json.dumps(updated_user),
        content_type='application/json',
    )

    data = json.loads(response.get_data(as_text=True))

    assert response.status_code == 200
    assert data == updated_user
    assert user_app.get_user_by_id(1) == updated_user


def test_api_delete_user(database, user):
    user_app.insert_user(user)

    response = user_app.app.test_client().delete('/api/users/delete/1')
    data = json.loads(response.get_data(as_text=True))

    assert response.status_code == 200
    assert data == {'status': 'User deleted successfully'}
    assert user_app.get_user_by_id(1) == {}
    assert user_app.get_users() == []