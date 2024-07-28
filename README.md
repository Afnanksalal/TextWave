## 🌊 TextWave
![Image Placeholder](textwave.png)
TextWave is your one-stop solution for transforming text into natural-sounding speech. With its support for diverse languages, accents, and customizable settings, you can unlock a world of possibilities. From crafting immersive games and enhancing accessibility to exploring new frontiers in creative expression, TextWave empowers you to bring your ideas to life through the magic of voice.

### ✨ Key Features

- **Text to Speech Magic:** Effortlessly convert written text into high-quality, lifelike speech.
- **Multilingual Mastery:** Break down language barriers with support for a wide range of languages and accents.
- **Tone & Style Customization:** Fine-tune your voice output to match the desired emotion and context.

### 🚀 Getting Started with TextWave

Before you use TextWave, ensure you have the following prerequisites:

* **Git:** For cloning the TextWave repository. [https://git-scm.com/](https://git-scm.com/)
* **Python 3.8+:** The programming language powering TextWave. [https://www.python.org/](https://www.python.org/)
* **Redis:** An in-memory data store used for rate limiting. [https://redis.io/](https://redis.io/)
* **MySQL:** A relational database for storing project-related data. [https://www.mysql.com/](https://www.mysql.com/)

Now, let's get TextWave up and running:

#### 1. Clone the Repository

Open your terminal or command prompt and execute the following command to download the TextWave source code:

```bash
git clone https://github.com/Afnanksalal/TextWave.git
```

#### 2. Set Up the Backend (Flask)

Navigate to the backend directory:

```bash
cd textwave/backend
```

* **Environment Variables:** Create a `.env` file in this directory and populate it with your Redis configuration details:

   ```
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_PASSWORD=your_redis_password
   REDIS_SSL=True
   ```

* **Install Dependencies:**  Use pip to install the necessary Python packages:

   ```bash
   pip install -r requirements.txt
   ```

   **Important:** During the installation, if you encounter any errors related to `unidic`, install it separately using:

   ```bash
   python -m unidic download
   ``` 
* **Download OpenVoice Checkpoint:**  
   - Download the checkpoint file from: [https://myshell-public-repo-hosting.s3.amazonaws.com/openvoice/checkpoints_v2_0417.zip](https://myshell-public-repo-hosting.s3.amazonaws.com/openvoice/checkpoints_v2_0417.zip)
   - Extract the contents and place the `checkpoint` directory in the root of your `backend` folder.

* **Launch the Backend:**

   ```bash
   python app.py
   ```

   By default, your Flask app will usually start on `http://127.0.0.1:5000/`. Note this URL, as you'll need it for the frontend.

#### 3. Configure the Frontend (Django)

Change directories to the frontend:

```bash
cd ../frontend 
```

* **Install Required Packages:**
   ```bash
   pip install django django-cors-headers mysqlclient 
   ```
* **Database Settings:** Open the `settings.py` file.  Within the `DATABASES` dictionary, update the settings for the 'default' connection to match your MySQL credentials:

   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'your_database_name',
           'USER': 'your_database_user',
           'PASSWORD': 'your_database_password',
           'HOST': 'your_database_host', 
           'PORT': '3306', 
       }
   }
   ```

* **Connect to the Backend:** In the `flask_api.py` file, replace  `'http://your_backend_url'` with the actual URL of your running Flask backend (e.g., `http://127.0.0.1:5000/`).


* **Run Database Migrations:**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

* **Start the Development Server:**

   ```bash
   python manage.py runserver
   ```

   Your Django development server will typically run on `http://127.0.0.1:8000/`.

**Installing FFmpeg:**

- **Instructions Vary:** The best way to install FFmpeg depends on your operating system (Windows, macOS, or Linux).
- **Official Website:** I recommend referring to the official FFmpeg download page for the most up-to-date instructions: [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)

Once you have FFmpeg installed, your system should be able to work with the audio processing tasks within TextWave. 
