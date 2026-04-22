**For backend -**
  cd backend

  create .env file same .env.Example
  
  python -m venv venv
  source venv/Scripts/activate
  uvicorn main:app --reload 
        or
  uvicorn main:app --host 0.0.0.0 --port 8000

**For Frontend -** 
 cd frontend
 npm install
 npm run dev
