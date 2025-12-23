# AirKicks | Full Stack E-Commerce Platform

I built this project last year for a university coursework module, but decided to upload it to GitHub now (in 2025) to show that I can build a proper **Full Stack applications** from scratch, rather than just using cloud services.

My main goal at the time was to create a shoe store that feels fast and sleek to use, with an array of different features, so I first focused on making the cart update instantly without the whole page reloading every time you click "add". I also included unique features like a **Sustainability Engine** which tracks the carbon footprint of the basket, thus allowing users to know that the products don't produce much pollution.

## Architecture

**User Session (Cookie) -> Flask Backend -> SQLAlchemy ORM -> SQLite Database -> AJAX Frontend**

- **User** When someone visits, I generate a random **UUID Session ID** and save it in their browser cookies, which is important as it allows them to have a cart that saves their items without them needing to create an account.
- **Brains** The **Flask** server handles all the routing and the logic for the carbon footprint math.
- **Data** I used **SQLAlchemy** to link the `Products` table to the `Carts` table, so I could easily find which items belonged to which user session.
- **UI** Instead of using normal HTML forms that reload the page, I used **JavaScript (AJAX)** to send data to the backend, which makes the site feel much smoother.

## Tech Stack

* **Backend:** Python 3, Flask, SQLAlchemy
* **Frontend:** HTML5, CSS3, JavaScript
* **Database:** SQLite
* **Key Libraries:** Flask-SQLAlchemy, Werkzeug

## How it works

The backend code, `app.py`, does most of the work, so here are the main things I implemented:

1. **The "Carbon" Engine** I added a `carbon_footprint` field to the Product database, so whenever the cart updates, the backend calculates the total CO₂ impact alongside the price, which gives the user a bit more info about their order.

2. **Guest Sessions** I didn't want to force people to login just to look around, so I wrote a function called `get_session_id()` that checks if they have a cookie, and if they don't it creates a new ID for them, which effectively links "guest" users to their data in the database.

3. **Search Logic** I made sure the search bar wasn't annoying to use by implementing a case-insensitive filter, so typing "Jordan" or "jordan" returns the same results.

## What I learned

- **"403 Forbidden" Bug** My "Add to Cart" button wouldn't work, and it turned out to be because my Flask route was checking for a specific security header, but my JavaScript `fetch` call wasn't sending it, so I manually added that header to my JS requests.

- **State Management** This project taught me how tricky it is to manage state when you don't have user accounts, as I needed to be careful to ensure that had a user left the site and came back, their cookie would still pull up the correct cart from the database.

- **"Self-Referencing" Logic** For the Recently Viewed section, I had a bug where the trainer you were currently looking at would appear in the "Recently Viewed" list, so I fixed this by adding a filter to exclude the current product ID from the list.

## 📂 Project Structure

```text
.
├── app.py              # Main Flask application logic
├── models.py           # Database schema
├── shop.db             # The SQLite database file
├── static/
│   ├── css/style.css   # Custom styling
│   └── js/script.js    # The AJAX logic for the cart
└── templates/          # Jinja2 HTML files
