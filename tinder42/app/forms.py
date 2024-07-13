class RegistrationForm:
    def __init__(self, email, username, last_name, first_name, password, confirm_password):
        self.email = email
        self.username = username
        self.last_name = last_name
        self.first_name = first_name
        self.password = password
        self.confirm_password = confirm_password
        self.errors = []

    def validate(self):
        if not self.email or '@' not in self.email:
            self.errors.append('Invalid email address.')
        if not self.username or len(self.username) < 2 or len(self.username) > 20:
            self.errors.append('Username must be between 2 and 20 characters.')
        if self.password != self.confirm_password:
            self.errors.append('Passwords do not match.')
        if len(self.password) < 6:
            self.errors.append('Password must be at least 6 characters long.')
        return len(self.errors) == 0

class LoginForm:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.errors = []

    def validate(self):
        if not self.email or '@' not in self.email:
            self.errors.append('Invalid email address.')
        if not self.password:
            self.errors.append('Password is required.')
        return len(self.errors) == 0

class UpdateProfileForm:
    def __init__(self, email, username, last_name, first_name, gender, sexual_preferences, biography='', location='', interests=''):
        self.email = email
        self.username = username
        self.last_name = last_name
        self.first_name = first_name
        self.gender = gender
        self.sexual_preferences = sexual_preferences
        self.biography = biography
        self.location = location
        self.interests = interests
        self.errors = []

    def validate(self):
        if not self.email or '@' not in self.email:
            self.errors.append('Invalid email address.')
        if not self.username or len(self.username) < 2 or len(self.username) > 20:
            self.errors.append('Username must be between 2 and 20 characters.')
        return len(self.errors) == 0

class MessageForm:
    def __init__(self, content):
        self.content = content
        self.errors = []

    def validate(self):
        if not self.content:
            self.errors.append('Message content is required.')
        return len(self.errors) == 0
