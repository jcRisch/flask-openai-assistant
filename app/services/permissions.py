import json

class PermissionsService:
    """
    Service class to handle permissions-related operations.
    """
    def __init__(self, user_data):
        self.user_data = user_data

    def get_user_data(self):
        """
        Return the user data in JSON format.
        """
        return self.user_data
    
    def get_permissions_by_user_id(self, user_id):
        """
        Collect and return the permissions of a user by their user ID in JSON format.
        """
        user = self.user_data.get(user_id)
        if not user:
            return "User not found"
    
        return json.dumps(user['permissions'])

    def get_user_id_by_username(self, username):
        """
        Return the user ID based on the username.
        """
        for user_id, info in self.user_data.items():
            if info['username'] == username:
                return user_id
        
        return None

    def update_user_permission(self, user_id, permission, value):
        """
        Update the value of a permission for a user by their user ID.
        """
        if user_id not in self.user_data:
            return "User not found"
        
        if permission not in self.user_data[user_id]['permissions']:
            return "Permission not found"
        
        self.user_data[user_id]['permissions'][permission] = value
        return "Permission updated"
