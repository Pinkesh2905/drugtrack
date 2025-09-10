
# DrugTrack Django Project

This guide will help you set up and run the **DrugTrack Django project** on your local machine. No prior technical knowledge is needed.

---

## **Step 1: Install Python**

1. Go to [Python Downloads](https://www.python.org/downloads/).  
2. Download **Python 3.13.x** (same version used in this project).  
3. During installation, **check “Add Python to PATH”**.  
4. Complete the installation.

---

## **Step 2: Extract the Project**

1. Download the `DrugTrack.zip` file.  
2. Right-click → **Extract All** to a folder, e.g., `C:\Projects\DrugTrack`.  
3. Make sure the folder contains `manage.py`, `requirements.txt`, and `run.bat`.

---

## **Step 3: Run the Project Using run.bat (Recommended)**

1. **Double-click** the `run.bat` file.  
2. The batch file will automatically:  
   - Create a virtual environment if it doesn’t exist.  
   - Install all required Python packages.  
   - Run database migrations.  
   - Start the Django development server.  
3. Wait until you see:

```

Starting development server at [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

```

4. Open a browser and go to:

```

[http://127.0.0.1:8000/](http://127.0.0.1:8000/)

```

- Admin panel (optional):  

```

[http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

````

---

## **Step 4: Manual Setup (If run.bat doesn’t work)**

1. Open **Command Prompt** in the project folder.  
2. Create a virtual environment:

```
python -m venv myenv
````

3. Activate the virtual environment:

```
myenv\Scripts\activate
```

4. Install dependencies:

```
pip install --upgrade pip
pip install -r requirements.txt
```

5. Run database migrations:

```
python manage.py migrate
```

6. (Optional) Create a superuser for admin access:

```
python manage.py createsuperuser
```

7. Start the server:

```
python manage.py runserver
```

8. Open the browser and go to `http://127.0.0.1:8000/`.

---

## **Step 5: Using the Project**

* Browse drugs and their details.
* Verify drugs using the patient dashboard.
* Access admin panel if a superuser is created.

---
