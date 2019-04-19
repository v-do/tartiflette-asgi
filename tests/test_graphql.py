from starlette.testclient import TestClient
from tartiflette_starlette import Tartiflette


def test_graphql_get(client):
    response = client.get("/?query={ hello }")
    assert response.status_code == 200
    assert response.json() == {
        "data": {"hello": "Hello stranger"},
        "errors": None,
    }


def test_graphql_post(client):
    response = client.post("/?query={ hello }")
    assert response.status_code == 200
    assert response.json() == {
        "data": {"hello": "Hello stranger"},
        "errors": None,
    }


def test_graphql_post_json(client):
    response = client.post("/", json={"query": "{ hello }"})
    assert response.status_code == 200
    assert response.json() == {
        "data": {"hello": "Hello stranger"},
        "errors": None,
    }


def test_graphql_post_graphql(client):
    response = client.post(
        "/", data="{ hello }", headers={"content-type": "application/graphql"}
    )
    assert response.status_code == 200
    assert response.json() == {
        "data": {"hello": "Hello stranger"},
        "errors": None,
    }


def test_graphql_post_invalid_media_type(client):
    response = client.post(
        "/", data="{ hello }", headers={"content-type": "dummy"}
    )
    assert response.status_code == 415
    assert response.text == "Unsupported Media Type"


def test_graphql_put(client):
    response = client.put("/", json={"query": "{ hello }"})
    assert response.status_code == 405
    assert response.text == "Method Not Allowed"


def test_graphql_no_query(client):
    response = client.get("/")
    assert response.status_code == 400
    assert response.text == "No GraphQL query found in the request"


def test_graphql_invalid_field(client):
    response = client.post("/", json={"query": "{ dummy }"})
    assert response.status_code == 400
    assert response.json() == {
        "data": None,
        "errors": [
            {
                "locations": [{"column": 3, "line": 1}],
                "message": 'Cannot query field "dummy" on type "Query".',
            }
        ],
    }


def test_graphiql_get(client):
    response = client.get("/", headers={"accept": "text/html"})
    assert response.status_code == 200
    assert "<!DOCTYPE html>" in response.text


def test_graphiql_not_found(engine):
    ttftt = Tartiflette(engine=engine, graphiql=False)
    client = TestClient(ttftt)
    response = client.get("/", headers={"accept": "text/html"})
    assert response.status_code == 404
    assert response.text == "Not Found"


def test_add_graphql_route(app, ttftt):
    app.add_route("/graphql", ttftt)
    client = TestClient(app)
    response = client.get("/graphql?query={ hello }")
    assert response.status_code == 200
    assert response.json() == {
        "data": {"hello": "Hello stranger"},
        "errors": None,
    }


def test_graphql_context(auth_app, ttftt):
    """Test the access the `context["request"]`."""
    auth_app.add_route("/graphql", ttftt)
    client = TestClient(auth_app)
    response = client.post(
        "/graphql",
        json={"query": "{ whoami }"},
        headers={"Authorization": "Bearer 123"},
    )
    assert response.status_code == 200
    assert response.json() == {"data": {"whoami": "Jane"}, "errors": None}
