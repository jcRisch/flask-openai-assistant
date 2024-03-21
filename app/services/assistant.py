from openai import OpenAI
from config import Config
import time
from flask import current_app, session
import json

class AssistantService:
    def __init__(self):
        self.openAI = OpenAI(api_key=Config.OPENAI_KEY)

        self.assistant_name = 'IT Administrator Assistant'
        self.model_id= 'gpt-4-turbo-preview'
        self.instruction= 'You are an IT administrator. You are responsible for managing user permissions. You have a list of users and their permissions. You can get the permissions of a user by their username, update the permissions of a user by their username, and get the user ID based on the username. You can use the following functions: getPermissionsByUsername, updatePermissionsByUsername, getUserIdByUsername.'
        
        self.assistant = self.get_or_create_assistant()
        self.thread = self.get_or_create_thread()

    def get_or_create_assistant(self):
        if 'assistant_id' in session:
            current_app.logger.info('Getting assistant')
            return self.openAI.beta.assistants.retrieve(session['assistant_id'])
        else:
            current_app.logger.info('Creating assistant')
            assistant = self.create_assistant()
            session['assistant_id'] = assistant.id
            return assistant

    def get_or_create_thread(self):
        if 'thread_id' in session:
            current_app.logger.info('Getting thread')
            return self.openAI.beta.threads.retrieve(session['thread_id'])
        else:
            current_app.logger.info('Creating thread')
            thread = self.create_thread()
            session['thread_id'] = thread.id
            return thread
       
    def create_assistant(self):
        current_app.logger.info('Creating assistant')
        return self.openAI.beta.assistants.create(
            name=self.assistant_name,
            instructions=self.instruction,
            model=self.model_id,
            tools=[
                self.define_function__get_permissions_by_username(), 
                self.define_function__get_user_id_by_username(), 
                self.define_function__update_user_permission()
            ]
        )
    
    def create_thread(self):
        current_app.logger.info('Creating thread')
        return self.openAI.beta.threads.create()
    
    def add_message_to_thread(self, role, message):
        current_app.logger.info(f'Adding message to thread: {role}, {message}')
        return self.openAI.beta.threads.messages.create(
            thread_id=self.thread.id,
            role=role,
            content=message,
        )
    
    def run_assistant(self, message):
        current_app.logger.info(f'Running assistant: {message}')
        message = self.add_message_to_thread("user", message)
        action_response = None

        run = self.openAI.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id,
        )
        run = self.wait_for_update(run)

        if run.status == "failed":
            current_app.logger.info('Run failed')
            return None
        elif run.status == "requires_action":
            current_app.logger.info(f'Run requires action: {run}')
            action_response = self.handle_require_action(run)
        else:
            current_app.logger.info('Run completed')
            action_response = self.get_last_assistant_message()

        return action_response
        
    def handle_require_action(self, run):
        current_app.logger.info('Handling required action')
        # Get the tool outputs by executing the required functions
        tool_calls = run.required_action.submit_tool_outputs.tool_calls
        current_app.logger.info(tool_calls)
        tool_outputs = self.generate_tool_outputs(tool_calls)

        # Submit the tool outputs back to the Assistant
        run = self.openAI.beta.threads.runs.submit_tool_outputs(
            thread_id=self.thread.id,
            run_id=run.id,
            tool_outputs=tool_outputs
        )
        
        run = self.wait_for_update(run)

        if run.status == "failed":
            current_app.logger.info('Run failed')
            return None
        elif run.status == "completed":
            return self.get_last_assistant_message()
        
    def wait_for_update(self, run):
        while run.status == "queued" or run.status == "in_progress":
            run = self.openAI.beta.threads.runs.retrieve(
                thread_id=self.thread.id,
                run_id=run.id,
            )
            time.sleep(1)
            current_app.logger.info(run.status)

        return run
    
    def get_last_assistant_message(self):
        current_app.logger.info('Getting last assistant message')
        messages = self.openAI.beta.threads.messages.list(thread_id=self.thread.id)
        if messages.data[0].role == 'assistant':
            message = messages.data[0]
            for content_block in message.content:
                if content_block.type == 'text':
                    return content_block.text.value
        else:
            return None
        
    def generate_tool_outputs(self, tool_calls):
        current_app.logger.info('Generating tool outputs')
        tool_outputs = []

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            arguments = tool_call.function.arguments
            tool_call_id = tool_call.id

            args_dict = json.loads(arguments)

            if hasattr(self, function_name):
                function_to_call = getattr(self, function_name)
                output = function_to_call(**args_dict) 

                tool_outputs.append({
                    "tool_call_id": tool_call_id,
                    "output": output,
                })

        return tool_outputs
    
    def define_function__get_user_id_by_username(self):
        function = {
            "type": "function",
            "function": {
                "name": "getUserIdByUsername",
                "description": "Get the user ID based on the username.",
                "parameters": {
                "type": "object",
                "properties": {
                    "username": {"type": "string", "description": "The username of the user."}
                },
                "required": ["username"]
                }
            }
        }
        return function
    
    def define_function__get_permissions_by_username(self):
        function = {
            "type": "function",
            "function": {
                "name": "getPermissionsByUsername",
                "description": "Get the permissions of a user by their username.",
                "parameters": {
                "type": "object",
                "properties": {
                    "username": {"type": "string", "description": "The username of the user."}
                },
                "required": ["username"]
                }
            }
        }
        return function
    
    def define_function__update_user_permission(self):
        function = {
            "type": "function",
            "function": {
                "name": "updateUserPermission",
                "description": "Update the value of a permission for a user by their username.",
                "parameters": {
                "type": "object",
                "properties": {
                    "username": {"type": "string", "description": "The username of the user."},
                    "permission": {"type": "string", "description": "The permission to update."},
                    "value": {"type": "boolean", "description": "The new value of the permission."}
                },
                "required": ["username"]
                }
            }
        }
        return function
    
    def getUserIdByUsername(self, username):
        current_app.logger.info(f'getUserIdByUsername: {username}')
        user_id = current_app.permissions_service.get_user_id_by_username(username)
        if user_id:
            current_app.logger.info(f'User found with id: {user_id}')
            return user_id
        else:
            current_app.logger.info('User not found')
            return "No user found"
    
    def getPermissionsByUsername(self, username):
        current_app.logger.info(f'getPermissionsByUsername: {username}')
        user_id = current_app.permissions_service.get_user_id_by_username(username)
        if user_id:
            current_app.logger.info(f'User found with id: {user_id}')
            permissions = current_app.permissions_service.get_permissions_by_user_id(user_id)
            current_app.logger.info(permissions)
            return permissions
        current_app.logger.info('User not found')
        return "No user found"
    
    def updateUserPermission(self, username, permission, value):
        current_app.logger.info(f'updateUserPermission: {username}, {permission}, {value}')
        user_id = current_app.permissions_service.get_user_id_by_username(username)
        if user_id:
            current_app.logger.info(f'User found with id: {user_id}')
            updated_permission = current_app.permissions_service.update_user_permission(user_id, permission, value)
            current_app.logger.info(updated_permission) 
            return updated_permission
        else:
            current_app.logger.info('User not found')
            return "No user found"