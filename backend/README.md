# Matcha - Dating Website

A dating website application built with FastAPI and Next.js.

## Backend Features

- User authentication (register, login, email verification, password reset)
- User profiles with tags, pictures, and geolocation
- Smart matching algorithm based on preferences, location, and tags
- Real-time chat between connected users
- Real-time notifications
- Profile interactions (like, visit, block, report)

## Tech Stack

### Backend

- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework for building APIs
- [SQLAlchemy](https://www.sqlalchemy.org/) - SQL toolkit and ORM
- [PostgreSQL](https://www.postgresql.org/) - Relational database
- [WebSockets](https://websockets.readthedocs.io/) - Real-time communication
- [Alembic](https://alembic.sqlalchemy.org/) - Database migrations

### Frontend (to be implemented)

- [Next.js](https://nextjs.org/) - React framework for building web applications

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL
- Node.js and npm (for frontend)

### Backend Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/matcha.git
cd matcha
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file based on the provided sample:

```bash
cp .env.sample .env
# Edit the .env file with your own configuration
```

5. Create the database:

```bash
# In PostgreSQL
createdb matcha
```

6. Apply migrations:

```bash
alembic upgrade head
```

7. Start the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000.
The API documentation will be available at http://localhost:8000/docs.

## Project Structure

```
matcha/
├── alembic/               # Database migrations
├── app/
│   ├── api/               # API endpoints
│   ├── core/              # Core configuration
│   ├── models/            # Database models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic
│   ├── templates/         # Email templates
│   └── main.py            # FastAPI application
├── media/                 # User uploads
│   └── profile_pictures/  # Profile pictures
├── .env                   # Environment variables
├── .gitignore             # Git ignore file
├── README.md              # Project documentation
├── alembic.ini            # Alembic configuration
└── requirements.txt       # Dependencies
```

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Log in a user
- `GET /api/auth/verify` - Verify email
- `POST /api/auth/forgot-password` - Request password reset
- `POST /api/auth/reset-password` - Reset password
- `POST /api/auth/change-password` - Change password
- `POST /api/auth/logout` - Log out

### Users

- `GET /api/users/me` - Get current user
- `PUT /api/users/me` - Update current user
- `POST /api/users/heartbeat` - Update user's online status

### Profiles

- `GET /api/profiles/me` - Get current user's profile
- `PUT /api/profiles/me` - Update current user's profile
- `PUT /api/profiles/me/tags` - Update profile tags
- `PUT /api/profiles/me/location` - Update profile location
- `POST /api/profiles/me/pictures` - Upload profile picture
- `DELETE /api/profiles/me/pictures/{picture_id}` - Delete profile picture
- `PUT /api/profiles/me/pictures/{picture_id}/primary` - Set primary picture
- `GET /api/profiles/suggested` - Get suggested profiles
- `GET /api/profiles/{profile_id}` - Get a profile

### Interactions

- `POST /api/interactions/like` - Like a profile
- `DELETE /api/interactions/like/{profile_id}` - Unlike a profile
- `POST /api/interactions/block` - Block a profile
- `DELETE /api/interactions/block/{profile_id}` - Unblock a profile
- `POST /api/interactions/report` - Report a profile
- `GET /api/interactions/likes` - Get profiles that liked current user
- `GET /api/interactions/visits` - Get profiles that visited current user
- `GET /api/interactions/matches` - Get matched profiles

### Real-time

- `WebSocket /api/realtime/ws/{token}` - WebSocket connection for real-time features
- `GET /api/realtime/notifications` - Get notifications
- `GET /api/realtime/notifications/count` - Get unread notification count
- `POST /api/realtime/notifications/{notification_id}/read` - Mark notification as read
- `POST /api/realtime/notifications/read-all` - Mark all notifications as read
- `POST /api/realtime/messages` - Send a message
- `GET /api/realtime/messages/{user_id}` - Get messages with a user
- `GET /api/realtime/conversations` - Get recent conversations
- `GET /api/realtime/messages/unread/count` - Get unread message count

## License

This project is licensed under the MIT License.