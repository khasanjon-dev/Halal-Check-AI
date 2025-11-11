# 🕌 Halal Check AI — Fullstack Project (FastAPI + React + Docker)

An AI-powered halal verification web app that allows users to **upload an image or enter text** (e.g., ingredients,
product description), and the system processes it to determine whether the product is **Halal, Haram, or Doubtful**.

---

## 🚀 Features

- 🧠 AI-ready backend built with **FastAPI**
- ⚛️ Beautiful **React** frontend with live previews
- 📸 Upload product images or type text descriptions
- 🔄 Loading states with smooth UX
- 🐳 Fully **Dockerized** for local or production deployment
- 🔒 CORS configured for safe API access
- 📂 Uploaded files automatically saved in organized folders

---

## 🧱 Project Structure

```

halal-check-ai/
│
├── backend/
│   ├── main.py              # FastAPI backend with endpoints
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile           # Backend Docker image setup
│   └── uploads/
│       ├── images/          # Uploaded images
│       └── texts/           # Uploaded text files
│
├── frontend/
│   ├── src/
│   │   └── HalalCheckApp.js # React main component
│   ├── public/
│   │   └── index.html
│   ├── package.json
│   └── Dockerfile           # Frontend Docker image setup
│
└── docker-compose.yml        # Combined frontend + backend configuration

```

---

## ⚙️ Backend API (FastAPI)

### Base URL

```

[http://localhost:8000](http://localhost:8000)

````

### Endpoints

#### 🖼️ `POST /analyze-image`

Upload an image file to analyze.

**Form Data:**
| Field | Type | Required | Description |
|--------|------|-----------|--------------|
| `image` | file | ✅ | Image file (JPG, PNG, JPEG, GIF, WEBP) |

**Response Example:**

```json
{
  "status": "success",
  "message": "Image uploaded successfully: abc123.jpg",
  "filename": "abc123.jpg"
}
````

---

#### 📝 `POST /analyze-text`

Send product description text for analysis.

**Form Data:**

| Field  | Type   | Required | Description              |
|--------|--------|----------|--------------------------|
| `text` | string | ✅        | Product description text |

**Response Example:**

```json
{
  "status": "success",
  "message": "Text uploaded successfully: xyz789.txt",
  "filename": "xyz789.txt"
}
```

---

#### 🏠 `GET /`

Health check endpoint.

```json
{
  "message": "Upload API is running"
}
```

---

## 🧰 Local Development Setup

### 🐍 Backend (FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

The API will be available at **[http://localhost:8000](http://localhost:8000)**

---

### ⚛️ Frontend (React)

```bash
cd frontend
npm install
npm start
```

The web UI will be available at **[http://localhost:3000](http://localhost:3000)**

---

## 🐳 Docker Deployment

Make sure you have **Docker** and **Docker Compose** installed.

Run both frontend and backend together:

```bash
docker-compose up --build
```

Then open:

* Frontend → [http://localhost:3000](http://localhost:3000)
* Backend → [http://localhost:8000/docs](http://localhost:8000/docs) for Swagger UI

---

## 🧪 Testing the App

1. Open your browser at [http://localhost:3000](http://localhost:3000)
2. Upload an image or type a product description
3. Click **Analyze**
4. Wait for the response — backend will return status and message
5. The result card shows the backend’s response clearly

---

## 🧱 Technologies Used

| Layer                | Technology                             |
|----------------------|----------------------------------------|
| **Frontend**         | React, TailwindCSS, Lucide React Icons |
| **Backend**          | FastAPI, Python, python-magic          |
| **Containerization** | Docker, Docker Compose                 |
| **Web Server**       | Uvicorn                                |

---

## 🧼 File Upload Handling

* Uploaded **images** → stored in `backend/uploads/images/`
* Uploaded **text files** → stored in `backend/uploads/texts/`
* Each file gets a **unique UUID** filename to avoid conflicts

---

## 🔍 API Documentation (Swagger UI)

When backend is running, visit:

👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**

or

👉 **[http://localhost:8000/redoc](http://localhost:8000/redoc)**

to view automatically generated Swagger and ReDoc documentation.

---

## 🧠 Next Steps (AI Integration)

You can extend this project easily by:

* Adding a trained AI model for text/ingredient classification
* Using image OCR (e.g., `pytesseract`) to extract ingredients from uploaded photos
* Integrating a halal ingredient database (e.g., via public APIs)

---

## 🪪 License

This project is open source and available under the [MIT License](LICENSE).

---

**Made with ❤️ by Khasanjon**

```

---

Would you like me to include a **Dockerfile and docker-compose.yml** example in this same README so it’s fully self-contained? (so someone could clone and `docker-compose up` immediately)
```
