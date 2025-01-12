import requests
from requests.auth import HTTPBasicAuth

from faker import Faker

BASE_URL = "http://localhost:5000/api"

"""
In order to use this route testing script you have to start the flask application first.
If needed, adjust the BASE_URL.
"""

def test_create_user(name, email, password, *, expected):
    """Test the user creation route."""
    data = {
        "name": name,
        "email": email,
        "password": password
    }
    response = requests.post(
        f"{BASE_URL}/users", json=data
    )
    assert response.status_code == expected, f"Unexpected status code: {response.status_code}"
    return response.json().get('id')

def test_get_user(id, *, expected):
    """Test the user creation route."""
    response = requests.get(
        f"{BASE_URL}/users/{id}"
    )
    assert response.status_code == expected, f"Unexpected status code: {response.status_code}"

def test_get_users(*, expected):
    """Test the user creation route."""
    response = requests.get(
        f"{BASE_URL}/users"
    )
    assert response.status_code == expected, f"Unexpected status code: {response.status_code}"

def test_modify_user(*, expected, token, name=None, email=None, password=None):
    """Test the user creation route."""
    data = {}
    if name:
        data["name"] = name
    if email:
        data["email"] = email
    if password:
        data["password"] = password
    assert data, f'No new data is specified'

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.patch(
        f"{BASE_URL}/users", json=data, headers=headers
    )
    assert response.status_code == expected, f"Unexpected status code: {response.status_code}"
    return response.json().get('id')

def test_delete_user(*, token, expected):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(
        f"{BASE_URL}/users", headers=headers
    )
    assert response.status_code == expected, f"Unexpected status code: {response.status_code}"

def test_get_token(email, password, *, expected):
    """Test the token creation route."""
    auth = HTTPBasicAuth(email, password)
    response = requests.post(
        f"{BASE_URL}/tokens",
        auth=auth
    )
    assert response.status_code == expected, f"Unexpected status code: {response.status_code}"
    return response.json().get('token')

def test_revoke_token(token, *, expected):
    """Test the token revocation route."""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(f"{BASE_URL}/tokens", headers=headers)
    assert response.status_code == expected, f"Unexpected status code: {response.status_code}"

def test_create_category(name, *, token, expected):
    """Test creating a category."""
    headers = {"Authorization": f"Bearer {token}"}
    data = {"name": name}
    response = requests.put(f"{BASE_URL}/category", json=data, headers=headers)
    assert response.status_code == expected, f"Unexpected status code: {response.status_code}"
    return response.json().get("id")

def test_get_category(id, *, expected):
    """Test retrieving category."""
    response = requests.get(f"{BASE_URL}/category/{id}")
    assert response.status_code == expected, f"Unexpected status code: {response.status_code}"

def test_get_categories(*, expected):
    """Test retrieving categories."""
    response = requests.get(f"{BASE_URL}/category")
    assert response.status_code == expected, f"Unexpected status code: {response.status_code}"

def test_create_listing(*, title, price, description, token, expected, categoryID=None, category=None):
    """Test creating a listing."""
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "title": title,
        "price": price,
        "description": description,
    }
    if categoryID:
        data["categoryID"] = categoryID
    elif categoryID:
        data["category"] = category
    response = requests.put(f"{BASE_URL}/listings", json=data, headers=headers)
    assert response.status_code == expected, f"Unexpected status code: {response.status_code}"
    return response.json().get("id")

def test_get_listing(id, *, expected):
    """Test retrieving listing."""
    response = requests.get(f"{BASE_URL}/listings/{id}")
    assert response.status_code == expected, f"Unexpected status code: {response.status_code}"

def test_get_listings(*, expected):
    """Test retrieving listings."""
    response = requests.get(f"{BASE_URL}/listings")
    assert response.status_code == expected, f"Unexpected status code: {response.status_code}"

def test_modify_listing(*, expected, token, id, title=None, price=None, description=None, category=None, categoryID=None):
    """Test modifying listings"""
    data = {}
    if title:
        data["title"] = title
    if price:
        data["price"] = price
    if description:
        data["description"] = description
    if categoryID:
        data["categoryID"] = categoryID
    elif category:
        data["category"] = category
    assert data, f'No new data is specified'

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.patch(
        f"{BASE_URL}/listings/{id}/edit", json=data, headers=headers
    )
    assert response.status_code == expected, f"Unexpected status code: {response.status_code}"
    return response.json().get("id")

def test_buy_listing(id, *, token, expected):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/listings/{id}/buy", headers=headers)
    assert response.status_code == expected, f"Unexpected status code: {response.status_code}"

def test_delete_listing(id, *, token, expected):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(
        f"{BASE_URL}/listings/{id}", headers=headers
    )
    assert response.status_code == expected, f"Unexpected status code: {response.status_code}"

if __name__ == '__main__':

    fake = Faker()
    email = fake.email()
    password = fake.password(32)
    name = fake.user_name()

    # user routes without authorization
    id = test_create_user(name, email, password, expected=201)
    test_create_user(name+"1", email, password, expected=400) # same email
    test_create_user(name, 'invalid-email', password, expected=400) # invalid email
    test_create_user(name+"漢字", fake.email(), password, expected=400) # invalid name
    test_create_user(name+'2', fake.email(), fake.password(10), expected=400) # invalid password
    test_get_user(id, expected=200)
    test_get_users(expected=200)

    # token routes for authorization
    test_get_token(fake.email(), fake.password(), expected=401) # not a user
    token = test_get_token(email, password, expected=201) # is a user

    assert id == test_modify_user(expected=200, token=token, name=fake.user_name()) # modify name
    assert id == test_modify_user(expected=200, token=token, email=fake.email()) # modify email
    assert id == test_modify_user(expected=200, token=token, password=fake.password(32)) # modify password
    test_modify_user(expected=200, token=token, email=email) # return email to original

    # category routes
    cat_id = test_create_category(name, token=token, expected=201)
    test_get_category(cat_id, expected=200)
    test_get_categories(expected=200)
    
    # listing routes
    listing_id = test_create_listing(title=fake.word(), price="10000,00", description=fake.sentence(),
                                     categoryID=cat_id, token=token, expected=201) # valid listing
    test_create_listing(title=fake.word(), price="1234", description=fake.sentence(),
                        category="does not exist", token=token, expected=400) # fake category (invalid listing)
    test_get_listing(listing_id, expected=200)
    test_get_listings(expected=200)

    assert listing_id == test_modify_listing(expected=200, token=token, id=listing_id, title=fake.word())
    assert listing_id == test_modify_listing(expected=200, token=token, id=listing_id, price="123456")
    assert listing_id == test_modify_listing(expected=200, token=token, id=listing_id, description=fake.sentence())
    assert listing_id == test_modify_listing(expected=200, token=token, id=listing_id, categoryID=1)
    test_modify_listing(expected=400, token=token, id=listing_id, category="another fake category")

    # second user
    email2, password2 = fake.email(), fake.password(32)
    id2 = test_create_user(fake.user_name(), email2, password2, expected=201)
    token2 = test_get_token(email2, password2, expected=201)

    test_buy_listing(listing_id, token=token, expected=400) # can't buy your own
    test_buy_listing(listing_id, token=token2, expected=200) # someone else can
    test_buy_listing(listing_id, token=token2, expected=400) # can't buy an already bought listing

    # deletion routes
    test_delete_user(token=token2, expected=204)
    test_delete_listing(id=listing_id, token=token, expected=204)
    
    # user deletion routes
    listing_id = test_create_listing(title=fake.word(), price="99,99", description=fake.sentence(),
                                     categoryID=cat_id, token=token, expected=201) # new listing to check if its deleted
    test_delete_user(token=token, expected=204)
    test_revoke_token(token, expected=401) # unauthorized
    test_get_listing(listing_id, expected=404) # not found


    print("All tests passed!")
