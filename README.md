# Project Name

A full-stack web application built with FastAPI backend and Next.js frontend.

## Features

- Feature 1
- Feature 2
- Feature 3

## Prerequisites

- Node.js (v14 or higher)
- Python (v3.8 or higher)
- pip (Python package manager)
- npm (Node package manager)

## Installation

### Backend Setup

1. Clone the repository:
```
git clone https://github.com/username/project.git
cd project
```

2. Create and activate virtual environment:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
3. Install dependencies:
```
cd backend
pip install -r requirements.txt
```

4. Configure environment variables:
Create .env file in backend directory
Add required environment variables:

```
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
SECRET_KEY=your_secret_key
```

5. Start the backend server:
```
uvicorn main:app --reload
```

### Frontend Setup

1. Navigate to frontend directory:
```
cd frontend
```

2. Install dependencies:
```
npm install
```

3. Configure environment variables:
- Create .env.local file in frontend directory:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. Start development server:
```
npm run dev
```

### Development

- Backend runs on: http://localhost:8000
- Frontend runs on: http://localhost:3000
- API documentation: http://localhost:8000/docs
