# Matcha

A modern dating web application inspired by Tinder, built as part of 42 School's curriculum.

## Tech Stack

- Frontend: Next.js
- Backend: FastApi
- Database: PostgreSQL
- Real-time: Socket.io
- Authentication: JWT

## Prerequisites

- Node.js (v14 or higher)
- Python (v3.8 or higher)
- pip (Python package manager)
- npm (Node package manager)

### Development

- Backend runs on: http://localhost:8000
- Frontend runs on: http://localhost:3000
- API documentation: http://localhost:8000/docs


## ✅ Project Checklist - Matcha Dating Website

### 📌 General Requirements

🤔   No errors, warnings, or notices (server-side & client-side)
🤔   Use any programming language and micro-framework of choice
✅   Use a relational or graph-oriented database (MySQL, PostgreSQL, Neo4j, etc.)
✅   Ensure database contains at least 500 distinct profiles
❌   Use a secure and well-structured UI (React, Vue, Bootstrap, etc.)
✅  Ensure website is mobile-friendly
✅   Implement proper form validation
✅   Prevent security vulnerabilities (SQL injection, XSS, plain-text passwords)
✅   Store credentials, API keys, and environment variables in .env file (excluded from Git)

### 📝 Mandatory Features

#### 🛂 Registration and Signing-in

✅   Allow users to register with:
	✅   Email
	✅   Username
	✅   Last Name
	✅   First Name
	✅   Secure password (no common words)
✅   Send email verification upon registration
✅   Allow users to log in with username & password
✅   Implement password reset via email
✅   Ensure users can log out from any page easily

#### 🏠 User Profile

🤔   Require users to complete profile with:
	✅   Gender
	✅   Sexual Preferences
	✅   Biography
	✅   Interest tags (e.g., #geek, #vegan)
	✅   Upload up to 5 pictures (one as profile picture)
✅   Allow users to update their profile information anytime
✅   Show who viewed their profile
✅   Show who liked their profile
✅   Implement public "fame rating" for each user
❌   Determine user location via GPS (with manual override option)
🤔   If GPS tracking is disabled, use an alternative location method

#### 🔍 Browsing

✅   Display suggested profiles based on:
	✅   Sexual orientation
	✅   Geographical proximity
	✅   Shared interest tags
	✅   "Fame rating"
✅   Allow sorting of profiles by:
	✅   Age
	✅   Location
	✅   "Fame rating"
	✅   Common tags
✅   Allow filtering by:
	✅   Age
	✅   Location
	✅   "Fame rating"
	✅   Common tags

#### 🔬 Research (Advanced Search)

🤔   Allow users to search with criteria:
	🤔   Age range
	🤔   "Fame rating" range
	🤔   Location
	🤔   Interest tags
🤔   Allow sorting and filtering in search results

#### 👀 Profile View

✅   Display all public profile information (except email/password)
✅   Track profile visit history
✅   Allow users to:
	✅   "Like" a profile (mutual likes enable chat)
	✅   Remove a "like" (disables chat & notifications)
	✅   Check another user’s fame rating
	✅   See online status & last active time
	✅   Report fake accounts
	✅   Block users (removes from search & disables chat)

#### 💬 Chat

✅   Enable real-time chat (only for mutually "liked" users)
✅   Display new messages notification on any page
✅   Ensure chat messages update within 10 seconds

#### 🔔 Notifications

✅   Notify users when:
	🤔   They receive a new like
	✅   Their profile is viewed
	✅   They receive a new message
	✅   A "liked" user likes them back
	🤔   A connected user "unlikes" them
✅   Display unread notifications on all pages
✅   Ensure notifications update within 10 seconds