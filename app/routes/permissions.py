from flask import render_template, Blueprint, request, current_app

permissions_bp = Blueprint('permissions', __name__)

@permissions_bp.route('/')
def home():
    title = "Ma Page d'Accueil"
    items = ['Pommes', 'Oranges', 'Bananes', 'Mangues']
    return render_template('home.html', title=title, items=items)

@permissions_bp.route('/user/<int:username>/permissions')
def user_permissions(user_id):
    username = 'User' + str(user_id)
    json_response = {'username': username, 'permissions': 'read'}
    return render_template('json.html', json_response=json_response)


@permissions_bp.route('/permissions/<username>', methods=['GET'])
def get_permissions(username):
    """
    Endpoint to return the permissions of a user by their username.
    """
    # Get user ID by username
    user_id_response = current_app.permissions_service.get_user_id_by_username(username)
    if user_id_response[1] != 200:
        return render_template('json.html', json_response=user_id_response[0]), user_id_response[1]
    
    user_id = user_id_response[0]['user_id']
    
    # Get permissions by user ID
    permissions_response = current_app.permissions_service.get_permissions_by_user_id(user_id)
    return render_template('json.html', json_response=permissions_response[0]), permissions_response[1]

@permissions_bp.route('/permissions/<username>/update', methods=['POST'])
def update_permissions(username):
    """
    Endpoint to update a user's permission by their username.
    """
    # Ensure request is JSON and has required data
    if not request.json or 'permission' not in request.json or 'value' not in request.json:
        return render_template('json.html', json_response={'error': 'Bad request, JSON body with "permission" and "value" required'}), 400
    
    permission = request.json['permission']
    value = request.json['value']
    
    # Get user ID by username
    user_id_response = current_app.permissions_service.get_user_id_by_username(username)
    if user_id_response[1] != 200:
        return render_template('json.html', json_response=user_id_response[0]), user_id_response[1]
    
    user_id = user_id_response[0]['user_id']
    
    # Update permission for the user
    update_response = current_app.permissions_service.update_user_permission(user_id, permission, value)
    return render_template('json.html', json_response=update_response[0]), update_response[1]