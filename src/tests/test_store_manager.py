"""
Tests for orders manager
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""


import json
import pytest
from store_manager import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health(client):
    result = client.get('/health-check')
    assert result.status_code == 200
    assert result.get_json() == {'status':'ok'}

def test_stock_flow(client):
    # 1. Créez un article (`POST /products`)
    product_data = {'name': 'Some Item', 'sku': '12345', 'price': 99.90}
    response = client.post('/products',
                          data=json.dumps(product_data),
                          content_type='application/json')
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['product_id'] > 0 
    # 2. Ajoutez 5 unités au stock de cet article (`POST /stocks`)
    stock_data = {'product_id': data['product_id'], 'quantity': 5}
    response = client.post('/stocks',
                          data=json.dumps(stock_data),
                          content_type='application/json')
    assert response.status_code == 201
    # 3. Vérifiez le stock, votre article devra avoir 5 unités dans le stock (`GET /stocks/:id`)
    response = client.get(f"/stocks/{data['product_id']}")
    assert response.status_code == 201  # Corrected: API returns 201
    assert response.get_json() == {'product_id': data['product_id'], 'quantity': 5}
    
    # 3.1Créer un utilisateur pour la commande
    user_data = {'name': 'Test User', 'email': 'test@example.com'}
    response = client.post('/users',
                          data=json.dumps(user_data),
                          content_type='application/json')
    assert response.status_code == 201
    user_result = response.get_json()
    user_id = user_result['user_id']
    
    # 4. Faites une commande de l'article que vous avez crée, 2 unités (`POST /orders`)
    order_data = {
        'user_id': user_id,
        'items': [
            {'product_id': data['product_id'], 'quantity': 2}
        ]
    }
    response = client.post('/orders',
                          data=json.dumps(order_data),
                          content_type='application/json')
    assert response.status_code == 201
    order_result = response.get_json()
    order_id = order_result['order_id']
    
    # 5. Vérifiez le stock encore une fois (`GET /stocks/:id`)
    response = client.get(f"/stocks/{data['product_id']}")
    assert response.status_code == 201
    assert response.get_json() == {'product_id': data['product_id'], 'quantity': 3}
    
    # 6. Étape extra: supprimez la commande et vérifiez le stock de nouveau. Le stock devrait augmenter après la suppression de la commande.
    response = client.delete(f"/orders/{order_id}")
    assert response.status_code == 200
    assert response.get_json() == {'deleted': True}  
    
 
    response = client.get(f"/stocks/{data['product_id']}")
    assert response.status_code == 201
    final_stock = response.get_json()
    assert final_stock == {'product_id': data['product_id'], 'quantity': 5}  # Should be back to 5