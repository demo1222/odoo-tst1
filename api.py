from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import random
from datetime import datetime, timedelta

app = FastAPI()

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, restrict this in production
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# Function to generate random shirt data
def generate_random_shirt_data(count=5):
    products = []

    design_styles = [
        "Modern",
        "Classic",
        "Minimal",
        "Vintage",
        "Abstract",
        "Geometric",
        "Floral",
        "Industrial",
        "Scandinavian",
        "Bohemian",
        "Rustic",
        "Contemporary",
        "Eclectic",
        "Art Deco",
        "Retro",
        "Futuristic",
        "Baroque",
        "Gothic",
        "Tropical",
        "Nautical",
        "Urban",
        "Traditional",
        "Mid-Century",
        "Pop Art",
        "Country",
        "Shabby Chic",
        "Oriental",
        "Mediterranean",
        "Victorian",
        "Zen",
    ] + [
        ""
    ] * 10  # Adding empty designs

    email_domains = [
        "gmail.com",
        "yahoo.com",
        "outlook.com",
        "hotmail.com",
        "example.com",
        "company.com",
        "business.org",
        "mail.net",
        "custom.io",
    ]

    names = [
        "Alice Johnson",
        "Brian Lee",
        "Catherine Nguyen",
        "Daniel Perez",
        "Emily Thompson",
        "George Smith",
        "Hannah Davis",
        "Isaac Moore",
        "Jasmine Patel",
        "Kyle Martinez",
    ]

    shirt_colors = ["White", "Black", "Navy", "Grey", "Red", "Green", "Blue", "Beige"]
    sizes = ["XS", "S", "M", "L", "XL", "XXL"]
    fit_types = ["Unisex", "Men", "Women", "Kids"]
    placements = ["Front Center", "Back", "Left Chest", "Right Sleeve", "Full Front"]
    notes_samples = [
        "Please use eco-friendly ink.",
        "This is a gift, make sure to hide price.",
        "Add the slogan in Comic Sans.",
        "Use faded/vintage effect.",
        "No text, only the image.",
        "Centered and large print, please.",
        "Place design on left side only.",
    ]
    photo_urls = [
        "https://example.com/designs/floral.jpg",
        "https://example.com/designs/dragon.png",
        "https://example.com/designs/logo.svg",
        "https://example.com/designs/comic.jpg",
        "https://example.com/designs/space.png",
        "https://example.com/designs/abstract.png",
        "https://example.com/designs/retro.png",
    ]

    addresses = [
        "123 Main St, New York, NY",
        "456 Oak Ave, Los Angeles, CA",
        "789 Pine Rd, Chicago, IL",
        "321 Maple Dr, Houston, TX",
        "555 Elm St, Miami, FL",
    ]

    start_date = datetime.now()

    for i in range(1, count + 1):
        item_id = random.randint(1, 1000)
        product_type = random.choice(["Shirt", "T-Shirt"])
        random_days = random.randint(-2, 0)
        random_date = (start_date + timedelta(days=random_days)).strftime("%Y-%m-%d")
        design = random.choice(design_styles)
        fast_ship = random.choice(["True"] + ["False"] * 9)

        quantity_weights = {i: max(1, 20 - i) for i in range(1, 21)}
        quantity_options = list(quantity_weights.keys())
        quantity_probabilities = [
            w / sum(quantity_weights.values()) for w in quantity_weights.values()
        ]
        quantity = random.choices(
            quantity_options, weights=quantity_probabilities, k=1
        )[0]

        email_prefix = f"user{random.randint(100, 999)}"
        email_domain = random.choice(email_domains)
        email = f"{email_prefix}@{email_domain}"

        # New data
        name = random.choice(names)
        shirt_color = random.choice(shirt_colors)
        size = random.choice(sizes)
        fit_type = random.choice(fit_types)
        placement = random.choice(placements)
        note = random.choice(notes_samples)
        photo = random.choice(photo_urls)
        address = random.choice(addresses)
        delivery_date = (start_date + timedelta(days=random.randint(3, 10))).strftime(
            "%Y-%m-%d"
        )

        product = {
            "id": item_id,
            "product": product_type,
            "date": random_date,
            "design": design,
            "fastShip": fast_ship,
            "quantity": quantity,
            "mail": email,
            "name": name,
            "shirtColor": shirt_color,
            "size": size,
            "fitType": fit_type,
            "designPlacement": placement,
            "notes": note,
            "photoURL": photo,
            "deliveryDate": delivery_date,
            "address": address,
        }

        products.append(product)

    return products


# API endpoint - returns 1-5 random items
@app.get("/api/get_data")
async def get_data():
    try:
        # Generate random number of items between 1 and 5
        count = random.randint(1, 10)
        print(f"Generating {count} random shirt data items.")
        data = generate_random_shirt_data(count)

        return JSONResponse(content={"status": "success", "data": data})
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)})


# API endpoint that returns a specific amount of data
@app.get("/api/get_data/{amount}")
async def get_random_data(amount: int):
    try:
        # Limit amount to reasonable range
        if amount < 1:
            amount = 1
        elif amount > 50:  # Set a reasonable upper limit
            amount = 50

        data = generate_random_shirt_data(amount)

        return JSONResponse(content={"status": "success", "data": data})
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)})


# Root endpoint for testing
@app.get("/")
async def root():
    return JSONResponse(
        content={
            "message": "Shirt API is running. Use /api/get_data to get random shirt data."
        }
    )
