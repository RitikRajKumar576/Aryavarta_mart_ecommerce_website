from django.shortcuts import render, get_object_or_404, redirect
from .models import (
    Brand,
    Product_Cards,
    Slideshow,
    Order,
    Category,
    Comingsoon,
    Dashboard_profile,
    Wishlist,
    Wishlist_product,
    Contact,
    State,
    ContactUs,
)
from django.http import JsonResponse
import json
from .forms import CheckoutForm, ComingsoonForm, ContactUsForm
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate, logout
import pandas as pd
from sklearn.ensemble import IsolationForest
import matplotlib

matplotlib.use("Agg")  # Use a non-GUI backend
import matplotlib.pyplot as plt
import io
import base64
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password

# import datetime
# from django.contrib.auth.decorators import login_required

# from .forms import

# Create your views here.


def register(request):
    categories = Category.objects.all()
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("index")
    else:
        form = UserCreationForm()
    context = {"form": form, "categories": categories}
    return render(request, "register.html", context)


def user_login(request):
    categories = Category.objects.all()
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You are now logged in.")
            return redirect("index")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("login")

    context = {"categories": categories}
    return render(request, "login.html", context)


def user_logout(request):
    logout(request)
    return redirect("index")


def index(request):
    categories = Category.objects.all()
    slideshow = Slideshow.objects.all()
    comingsoon = Comingsoon.objects.all()
    # Fetch active products from the 'Brand' model
    trending_products = Brand.objects.filter(status=True)

    # query = request.GET.get('q', '')
    # search_results = []
    # if query:
    #     ranked_products = smart_search(query)
    #     all_products = Brand.objects.all()
    #     search_results = [all_products[i] for i in ranked_products]
    context = {
        "categories": categories,
        "products": trending_products,
        "slideshow": slideshow,
        "comingsoon": comingsoon,
    }

    return render(request, "index.html", context)


def mobile(request):
    categories = Category.objects.all()
    return render(request, "mobile.html", {"categories": categories})


def category_products_view(request, slug):
    category = get_object_or_404(Category, slug=slug)  # Get current category
    products = Brand.objects.filter(
        category=category.name.lower(), status=True
    )  # Fetch products
    categories = Category.objects.all()  # Fetch all categories for dropdown

    context = {"category": category, "products": products, "categories": categories}
    return render(request, "category_products.html", context)


def category(request):
    categories = Category.objects.all()  # Fetch all categories

    if request.method == "POST":  # Handle the delete request
        category_id = request.POST.get(
            "category_id"
        )  # Get category ID from POST request
        if category_id:
            category = get_object_or_404(Category, id=category_id)
            category.delete()
            messages.success(request, "Category deleted successfully!")
            return redirect("category")  # Redirect to the category list page

    return render(request, "admin/category.html", {"categories": categories})


def alter_category(request, category_id=None):
    if category_id:  # If category_id is provided, edit the category
        category = get_object_or_404(Category, id=category_id)
    else:  # Otherwise, it's for adding a new category
        category = None

    if request.method == "POST":
        category_name = request.POST.get("category_name")  # Get category name from form

        # Adding category if not editing
        if not category:
            if category_name:
                category, created = Category.objects.get_or_create(name=category_name)
                if created:
                    messages.success(
                        request, f"Category '{category_name}' added successfully!"
                    )
                    return redirect("category")  # Redirect to category list page
                else:
                    messages.warning(
                        request, f"Category '{category_name}' already exists!"
                    )
            return redirect("alter_category")  # Redirect to the same page

        # Editing category if category_id is provided
        else:
            if category_name:
                category.name = category_name
                category.slug = request.POST.get("slug")  # Get the slug
                category.save()
                messages.success(request, "Category updated successfully!")
                return redirect("category")  # Redirect to category list page

    return render(request, "admin/alter_category.html", {"category": category})


def shop(request):
    categories = Category.objects.all()
    filter_option = request.GET.get("filter", "low_price")  # Get filter from the URL

    # Default product listing
    shop_products = Brand.objects.all()

    if filter_option == "low_price":
        shop_products = shop_products.order_by("price")  # Sorting by low price
    elif filter_option == "high_price":
        shop_products = shop_products.order_by("-price")  # Sorting by high price
    elif filter_option == "newly_added":
        shop_products = shop_products.order_by(
            "-id"
        )  # Sorting by the newest added items (ID assumed as creation order)

    context = {
        "shop_products": shop_products,
        "categories": categories,
    }
    return render(request, "shop.html", context)


def slideshow(request):
    slideshow = Slideshow.objects.all()
    return render(request, "admin/slideshow.html", {"slideshow": slideshow})



def contact_us(request):
    if request.method == "POST":
        form = ContactUsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('contact_us')  # Redirect to a success page
    else:
        form = ContactUsForm()
    context = {
        'form': form,
    }
    return render(request, "contact_us.html", context)



def load_states(request):
    country_id = request.GET.get('country_id')
    states = State.objects.filter(country_id=country_id).order_by('state')
    return render(request, 'state_dropdown_list.html', {'states': states})


def slideshowalter(request, item_id=None):
    """
    Handles add, update, and delete operations for Slideshow.
    """
    if request.method == "POST":
        # DELETE operation (if 'delete' is in the form)
        if "delete" in request.POST:
            slideshow = get_object_or_404(Slideshow, pk=item_id)
            slideshow.delete()
            return redirect("slideshow")

        # ADD or UPDATE operation
        if item_id:
            # Update existing item
            slideshow = get_object_or_404(Slideshow, pk=item_id)
        else:
            # Add new item
            slideshow = Slideshow()

        if "image" in request.FILES:
            slideshow.image = request.FILES["image"]
        slideshow.title = request.POST["title"]
        slideshow.caption = request.POST["caption"]
        slideshow.order = request.POST["order"]
        slideshow.save()
        return redirect("slideshow")

    # GET request: Render the form for Add or Edit
    if item_id:
        slideshow = get_object_or_404(Slideshow, pk=item_id)
    else:
        slideshow = None  # For adding a new product
    return render(
        request,
        "admin/edit_slideshow.html",
        {"slideshow": slideshow, "item_id": item_id},
    )


def productcards(request):
    products = Product_Cards.objects.all()
    return render(request, "admin/productcards.html", {"products": products})


def productcardsalter(request, item_id=None):
    """
    Handles add, update, and delete operations for Product_Cards.
    """
    if request.method == "POST":
        # DELETE operation (if 'delete' is in the form)
        if "delete" in request.POST:
            item = get_object_or_404(Product_Cards, pk=item_id)
            item.delete()
            return redirect("productcards")

        # ADD or UPDATE operation
        if item_id:
            # Update existing item
            item = get_object_or_404(Product_Cards, pk=item_id)
        else:
            # Add new item
            item = Product_Cards()

        if "image" in request.FILES:
            item.image = request.FILES["image"]
        item.heading = request.POST["heading"]
        item.price = request.POST["price"]
        item.description = request.POST["description"]
        item.save()
        return redirect("productcards")

    # GET request: Render the form for Add or Edit
    if item_id:
        item = get_object_or_404(Product_Cards, pk=item_id)
    else:
        item = None  # For adding a new product
    return render(
        request, "admin/edit_slideshow.html", {"item": item, "item_id": item_id}
    )


# def brandoffer(request):
#     brand = BrandOffer.objects.all()
#     return render(request,'admin/brandoffer.html',{'brand':brand})


# def alterbrandoffer(request, item_id=None):
#     """
#     Handles add, update, and delete operations for BrandOffer.
#     """
#     if request.method == 'POST':
#         # DELETE operation (if 'delete' is in the form)
#         if 'delete' in request.POST:
#             brand = get_object_or_404(BrandOffer, pk=item_id)
#             brand.delete()
#             return redirect('brandoffer')

#         # ADD or UPDATE operation
#         if item_id:
#             # Update existing item
#             brand = get_object_or_404(BrandOffer, pk=item_id)
#         else:
#             # Add new item
#             brand = BrandOffer()

#         if 'image' in request.FILES:
#             brand.image = request.FILES['image']
#         brand.brand = request.POST['brand']
#         brand.discount = request.POST['discount']
#         brand.description = request.POST['description']
#         brand.save()
#         return redirect('brandoffer')

#     # GET request: Render the form for Add or Edit
#     if item_id:
#         brand = get_object_or_404(BrandOffer, pk=item_id)
#     else:
#         brand = None  # For adding a new product
#     return render(request, 'admin/edit_brandoffer.html', {'brand': brand, 'item_id': item_id})


def dashboard_login(request):
    if request.method == "POST":
        if "login" in request.POST:  # Login form submission
            email = request.POST["email"]
            password = request.POST["password"]
            try:
                user = Dashboard_profile.objects.get(email=email)
                if check_password(password, user.password):
                    request.session["dashboard_user_id"] = user.id  # Store user session
                    return redirect("dashboard_panel")
                else:
                    return render(
                        request,
                        "admin/dashboard_login.html",
                        {"error": "Invalid credentials"},
                    )
            except Dashboard_profile.DoesNotExist:
                return render(
                    request, "admin/dashboard_login.html", {"error": "User not found"}
                )

        elif "register" in request.POST:  # Register form submission
            username = request.POST["username"]
            email = request.POST["email"]
            password = request.POST["password"]

            if Dashboard_profile.objects.filter(email=email).exists():
                return render(
                    request,
                    "admin/dashboard_login.html",
                    {"error": "Email already registered"},
                )

            # Save new user
            new_user = Dashboard_profile(
                username=username, email=email, password=make_password(password)
            )
            new_user.save()

            return render(
                request,
                "admin/dashboard_login.html",
                {"error": "Account created! Please login."},
            )

    return render(request, "admin/dashboard_login.html")


def dashboard_panel(request):
    # Check if user is authenticated through custom session
    user_id = request.session.get("dashboard_user_id")
    if not user_id:
        return redirect(
            "dashboard_login"
        )  # Redirect to login if user is not authenticated

    try:
        # Fetch user from the custom Dashboard_profile model
        user = Dashboard_profile.objects.get(id=user_id)
    except Dashboard_profile.DoesNotExist:
        return redirect("dashboard_login")  # Redirect to login if user does not exist

    # Get all active sessions
    active_sessions = Session.objects.filter(expire_date__gte=timezone.now())

    # Extract user IDs from active sessions
    logged_in_users = set()
    for session in active_sessions:
        data = session.get_decoded()
        dashboard_user_id = data.get("dashboard_user_id")
        if dashboard_user_id:
            logged_in_users.add(dashboard_user_id)

    # Count only logged-in users
    total_logged_in_users = len(logged_in_users)

    # Fetch total sales
    total_sales = (
        Brand.objects.aggregate(total_sales=Sum("price"))["total_sales"] or 0.0
    )

    # Fetch total orders
    total_orders = Order.objects.count()

    # Fetch recent orders (limit to last 5 orders)
    recent_orders = Order.objects.order_by("-ordered_at")[:]

    context = {
        "total_logged_in_users": total_logged_in_users,
        "total_sales": total_sales,
        "total_orders": total_orders,
        "recent_orders": recent_orders,  # Pass recent orders to template
        "username": user.username,  # Pass the username of the authenticated user
    }
    return render(request, "admin/admin.html", context)


def analytics(request):
    return render(request, "admin/analytics.html")


@csrf_exempt
def configure_order(request, order_id=None):
    if request.method == "POST":
        if "status" in request.POST:  # Handle status update
            order = get_object_or_404(Order, id=order_id)
            order.status = request.POST.get("status")
            order.save()
        elif "delete" in request.POST:  # Handle order deletion
            order = get_object_or_404(Order, id=order_id)
            order.delete()
        return redirect("configure_order")

    orders = Order.objects.all()
    return render(request, "admin/configure_order.html", {"orders": orders})



def add_country(request):
    contacts = Contact.objects.all()
    states = State.objects.all()  # Changed variable name to avoid conflict
    context = {
        "contacts": contacts,
        "states": states  # Make sure to pass 'states' to the template
    }
    return render(request, "admin/country.html", context)

def admin_settings(request):
    return render(request, "admin/setting.html")


def alter_country(request):
    if request.method == "POST":  # When form is submitted
        country_name = request.POST.get("country")
        state_name = request.POST.get("state")

        if country_name and state_name:  # Ensure both values are provided
            # Check if the country already exists
            country, created = Contact.objects.get_or_create(country=country_name)

            # Now, create the state linked to this country
            State.objects.create(country=country, state=state_name)

            return redirect("add_country")  # Redirect to the same page
        else:
            return JsonResponse({"error": "Both country and state are required."}, status=400)

    return render(request, "admin/add_country.html")

# @csrf_exempt
# def configure_order(request, order_id=None):
#     if request.method == "POST":
#         action = request.POST.get("action")
#         order_id = request.POST.get("order_id")

#         if action == "delete":
#             order = get_object_or_404(Order, id=order_id)
#             order.delete()
#             return redirect("configure_order")

#         elif action == "update_status":
#             order = get_object_or_404(Order, id=order_id)
#             order.status = request.POST.get("status")
#             order.save()
#             return redirect("configure_order")

#     # Fetch all orders
#     orders = Order.objects.all()
#     context = {
#         "orders": orders
#     }
#     return render(request, "admin/configure_order.html", context)




def view_contact_us(request):
    contact_us = ContactUs.objects.all()
    return render(request, 'admin/view_contact_us.html',{'contact_us':contact_us})


def brand(request):
    branditem = Brand.objects.all()
    return render(request, "admin/brand.html", {"branditem": branditem})


def comingsoon(request):
    comingsoonitem = Comingsoon.objects.all()
    context = {"comingsoonitem": comingsoonitem}
    return render(request, "admin/comingsoon.html", context)


def altercomingsoon(request):
    if request.method == "POST":  # When form is submitted
        form = ComingsoonForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("comingsoon")  # Redirect after saving
        else:
            return render(
                request, "admin/altercomingsoon.html", {"form": form}
            )  # If form is invalid
    else:
        form = ComingsoonForm()  # Display an empty form for GET request
        return render(request, "admin/altercomingsoon.html", {"form": form})


def alterbrand(request, item_id=None):
    """
    Handles add, update, and delete operations for Brand.
    """
    if request.method == "POST":
        # DELETE operation (if 'delete' is in the form)
        if "delete" in request.POST:
            brand = get_object_or_404(Brand, pk=item_id)
            brand.delete()
            return redirect("brand")

        # ADD or UPDATE operation
        if item_id:
            # Update existing item
            brand = get_object_or_404(Brand, pk=item_id)
        else:
            # Add new item
            brand = Brand()

        # Handle form data
        if "image" in request.FILES:
            brand.image = request.FILES["image"]
        brand.name = request.POST.get("name", "")
        brand.price = request.POST.get("price", 0.0)
        brand.category = request.POST.get("category", "mobile")
        brand.status = request.POST.get("status") == "on"

        brand.save()
        return redirect("brand")

    # GET request: Render the form for Add or Edit
    if item_id:
        brand = get_object_or_404(Brand, pk=item_id)
    else:
        brand = None  # For adding a new product
    return render(
        request, "admin/alterbrand.html", {"brand": brand, "item_id": item_id}
    )







@login_required
def wishlist(request):
    wishlist, created = Wishlist_product.objects.get_or_create(user=request.user)
    wishlist_products = wishlist.products.all()  # Get all products in wishlist

    categories = Category.objects.all()
    context = {
        "wishlist_products": wishlist_products,  # Use correct key for template
        "categories": categories,
    }
    return render(request, "wishlist.html", context)


@login_required
def add_to_wishlist(request, product_id):
    if request.method == "POST":  # Ensure it's a POST request
        product = get_object_or_404(Brand, id=product_id)
        wishlist, created = Wishlist_product.objects.get_or_create(user=request.user)

        if wishlist.products.filter(id=product.id).exists():
            return JsonResponse({"status": "exists"})  # Item is already in wishlist
        else:
            wishlist.products.add(product)
            return JsonResponse({"status": "added"})
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)


def remove_from_wishlist(request, product_id):
    if request.user.is_authenticated:
        try:
            wishlist = get_object_or_404(Wishlist_product, user=request.user)
            product = get_object_or_404(
                Brand, id=product_id
            )  # Get the product from Brand model

            if product in wishlist.products.all():
                wishlist.products.remove(product)  # Remove product from wishlist
                messages.success(request, "Item removed from wishlist.")
            else:
                messages.error(request, "Item not found in wishlist.")

        except Exception as e:
            messages.error(request, f"Error: {e}")

        return redirect("wishlist")  # Redirect back to wishlist page

    messages.error(request, "You must be logged in to remove items from your wishlist.")
    return redirect("login")


@csrf_exempt
def add_to_cart(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            product_id = str(data.get("product_id"))  # Ensure product_id is a string
            quantity = int(data.get("quantity"))  # Get quantity, default to 1

            cart = request.session.get("cart", {})

            if product_id in cart:
                cart[product_id] += quantity  # Add selected quantity
            else:
                cart[product_id] = quantity  # Set initial quantity

            request.session["cart"] = cart  # Update session

            return JsonResponse({"message": "Item added to cart", "cart": cart})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)


def remove_from_cart(request, product_id):
    cart = request.session.get("cart", {})

    # Convert product_id to a string as session keys are typically strings
    str_product_id = str(product_id)

    if str_product_id in cart:
        del cart[str_product_id]  # Remove the item from the cart

    # Save the updated cart back to the session
    request.session["cart"] = cart
    request.session.modified = True  # Ensure the session is saved immediately

    return redirect("my_cart")  # Redirect back to the cart page


def update_cart(request, item_id, new_quantity):
    # Get the cart from the session
    cart = request.session.get("cart", {})

    # If the product exists in the cart
    if str(item_id) in cart:
        cart[str(item_id)] = new_quantity  # Update the quantity in the cart

        # Recalculate total amount
        total_amount = Decimal(0)
        cart_items = []

        valid_product_ids = [int(k) for k in cart.keys() if k.isdigit()]
        products = Brand.objects.filter(id__in=valid_product_ids)

        for product in products:
            quantity = cart.get(str(product.id), 1)
            total_price = product.price * quantity
            product.quantity = quantity
            product.total_price = "{:,.2f}".format(total_price)
            cart_items.append(product)
            total_amount += total_price

        # Calculate 18% GST
        gst = total_amount * Decimal("0.18")
        total_with_gst = total_amount + gst

        # Format amounts for the response
        total_amount = "{:,.2f}".format(total_amount)
        gst = "{:,.2f}".format(gst)
        total_with_gst = "{:,.2f}".format(total_with_gst)

        # Return updated totals in the response
        return JsonResponse(
            {
                "success": True,
                "item_total_price": "{:,.2f}".format(product.price * new_quantity),
                "total_amount": total_amount,
                "gst": gst,
                "total_with_gst": total_with_gst,
            }
        )
    else:
        return JsonResponse({"success": False, "message": "Item not found in cart"})


def my_cart(request):
    categories = Category.objects.all()
    cart = request.session.get("cart", {})
    cart_items = []
    total_amount = Decimal(0)  # Initialize total amount as a Decimal

    if cart:
        # Only include valid numeric keys for the 'id' filter
        valid_product_ids = [int(k) for k in cart.keys() if k.isdigit()]

        # Fetch products by valid IDs
        products = Brand.objects.filter(id__in=valid_product_ids)

        for product in products:
            quantity = cart.get(
                str(product.id), 1
            )  # Get quantity from cart, default to 1
            total_price = product.price * quantity  # Calculate total price per item

            # Add extra attributes dynamically
            product.quantity = quantity
            product.total_price = "{:,.2f}".format(total_price)  # Format with commas

            cart_items.append(product)
            total_amount += total_price  # Add total item price to total amount

    else:
        # If the cart is empty, you can handle the case where no products are found
        pass

    # Calculate 18% GST
    gst = total_amount * Decimal("0.18")  # Convert 0.18 to Decimal
    total_with_gst = total_amount + gst

    # Format amounts with commas
    total_amount = "{:,.2f}".format(total_amount)
    gst = "{:,.2f}".format(gst)
    total_with_gst = "{:,.2f}".format(total_with_gst)

    context = {
        "cart_items": cart_items,
        "total_amount": total_amount,
        "gst": gst,
        "total_with_gst": total_with_gst,
        "categories": categories,
    }

    return render(request, "mycart.html", context)


# def my_cart(request):
#     cart = request.session.get("cart", {})
#     cart_items = []
#     total_amount = 0  # Initialize total amount

#     if cart:
#         # Only include valid numeric keys for the 'id' filter
#         valid_product_ids = [int(k) for k in cart.keys() if k.isdigit()]

#         # Fetch products by valid IDs
#         products = Brand.objects.filter(id__in=valid_product_ids)

#         for product in products:
#             quantity = cart.get(str(product.id), 1)  # Get quantity from cart, default to 1
#             total_price = product.price * quantity  # Calculate total price per item

#             # Add extra attributes dynamically
#             product.quantity = quantity
#             product.total_price = "{:,.2f}".format(total_price)  # Format with commas

#             cart_items.append(product)
#             total_amount += total_price  # Add total item price to total amount
#     else:
#         # If the cart is empty, you can handle the case where no products are found
#         pass

#     total_amount = "{:,.2f}".format(total_amount)  # Format total amount with commas

#     return render(request, "mycart.html", {"cart_items": cart_items, "total_amount": total_amount})

# def my_cart(request):
#     cart = request.session.get("cart", {})
#     cart_items = []
#     total_amount = 0  # Initialize total amount

#     if cart:
#         products = Brand.objects.filter(
#             id__in=cart.keys()
#         )  # Fetch products by IDs in the cart

#         for product in products:
#             quantity = cart.get(str(product.id))  # Get quantity from cart, default to 1
#             total_price = product.price * quantity  # Calculate total price per item

#             # Add extra attributes dynamically
#             product.quantity = quantity
#             product.total_price = "{:,.2f}".format(total_price)  # Format with commas

#             cart_items.append(product)
#             total_amount += total_price  # Add total item price to total amount
#     else:
#         valid_product_ids = [int(k) for k in cart.keys() if k.isdigit()]  # Only numbers

#         if valid_product_ids:
#             products = Brand.objects.filter(id__in=valid_product_ids)
#             for product in products:
#                 quantity = cart.get(str(product.id), 1)
#                 total_price = product.price * quantity
#                 cart_items.append({
#                     "id": product.id,  # Ensure ID is included
#                     "product": product,
#                     "quantity": quantity,
#                     "total_price": total_price,
#                 })
#                 total_amount += total_price

#     total_amount = "{:,.2f}".format(total_amount)  # Format total amount with commas

#     return render(request, "mycart.html", {"cart_items": cart_items, "total_amount": total_amount})


# def update_cart(request, item_id, new_quantity):
#     cart = request.session.get("cart", {})

#     if str(item_id) in cart:
#         cart[str(item_id)] = new_quantity  # Update quantity in session
#         request.session["cart"] = cart  # Save session

#         # Recalculate totals
#         products = Brand.objects.filter(id__in=cart.keys())
#         total_amount = 0
#         item_total_price = 0

#         for product in products:
#             quantity = cart[str(product.id)]
#             total_price = product.price * quantity
#             if product.id == int(item_id):
#                 item_total_price = total_price  # Get updated price for this item
#             total_amount += total_price  # Update total amount

#         return JsonResponse(
#             {
#                 "success": True,
#                 "item_total_price": f"{item_total_price:,.2f}",
#                 "total_amount": f"{total_amount:,.2f}",
#             }
#         )

#     return JsonResponse({"success": False})


# Assuming you have an Order model to save order details


def checkout(request):
    categories = Category.objects.all()
    if request.method == "POST":
        # Get cart data from session
        cart = request.session.get("cart", {})
        cart_items = []
        total_amount = 0
        valid_product_ids = [int(k) for k in cart.keys() if k.isdigit()]
        products = Brand.objects.filter(id__in=valid_product_ids)

        for product in products:
            quantity = cart.get(str(product.id), 1)
            total_price = product.price * quantity
            cart_items.append(
                {
                    "product": product,
                    "quantity": quantity,
                    "total_price": total_price,
                }
            )
            total_amount += total_price

        # Calculate GST and total with GST
        gst = total_amount * Decimal("0.18")
        total_with_gst = total_amount + gst

        # Process the checkout form
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Save order details for each item in the cart
            for item in cart_items:
                order = Order(
                    brand=item["product"],  # Save each product separately
                    customer_name=form.cleaned_data["full_name"],
                    customer_email=form.cleaned_data["email"],
                    customer_address=form.cleaned_data["address"],
                    phone=form.cleaned_data["phone"],
                    payment_method=form.cleaned_data["payment_method"],
                    card_number=(
                        form.cleaned_data["card_number"]
                        if form.cleaned_data["payment_method"] == "credit-card"
                        else None
                    ),
                    card_expiry=(
                        form.cleaned_data["card_expiry"]
                        if form.cleaned_data["payment_method"] == "credit-card"
                        else None
                    ),
                    cvv=(
                        form.cleaned_data["cvv"]
                        if form.cleaned_data["payment_method"] == "credit-card"
                        else None
                    ),
                    quantity=item["quantity"],  # Save the correct quantity per item
                    total_price=item[
                        "total_price"
                    ],  # Save price per item, not total cart price
                )
                order.save()

            # Clear the cart after placing the order
            request.session["cart"] = {}
            messages.success(request, "Your order has been placed successfully!")
            return redirect(
                "order_confirmation"
            )  # Redirect to the order confirmation page

    else:
        form = CheckoutForm()
    context = {
        "categories": categories,
        "form": form,
    }
    return render(request, "checkout.html", context)


def order_confirmation(request):
    categories = Category.objects.all()
    # Ensure the page is only shown when the order is successfully placed
    if not request.user.is_authenticated:
        return redirect("index")  # Redirect to homepage if not authenticated
    else:
        return render(request, "order_confirmation.html", {"categories": categories})


# def checkout(request):
#     if request.method == "POST":
#         form = CheckoutForm(request.POST)
#         if form.is_valid():
#             # Get form data
#             full_name = form.cleaned_data["full_name"]
#             email = form.cleaned_data["email"]
#             address = form.cleaned_data["address"]
#             phone = form.cleaned_data["phone"]
#             payment_method = form.cleaned_data["payment_method"]
#             card_number = form.cleaned_data.get("card_number")
#             card_expiry = form.cleaned_data.get("card_expiry")
#             cvv = form.cleaned_data.get("cvv")
#             upi_method = form.cleaned_data.get("upi_method")

#             # Process payment here, save order to the database, etc.
#             order = Order.objects.create(
#                 full_name=full_name,
#                 email=email,
#                 address=address,
#                 phone=phone,
#                 payment_method=payment_method,
#                 card_number=card_number if payment_method == "credit-card" else None,
#                 card_expiry=card_expiry if payment_method == "credit-card" else None,
#                 cvv=cvv if payment_method == "credit-card" else None,
#                 upi_method=upi_method if payment_method == "upi" else None,
#             )

#             # Redirect to a success page after saving the order
#             return render(request, "checkout_success.html", {"order": order})
#     else:
#         form = CheckoutForm()

#     return render(request, "checkout.html", {"form": form})


# def checkout(request):
#     if request.method == 'POST':
#         form = CheckoutForm(request.POST)
#         if form.is_valid():
#             # Extract form data
#             customer_name = form.cleaned_data['customer_name']
#             customer_email = form.cleaned_data['customer_email']
#             customer_address = form.cleaned_data['customer_address']
#             phone = form.cleaned_data['phone']
#             payment_method = form.cleaned_data['payment_method']
#             card_number = form.cleaned_data.get('card_number')
#             card_expiry = form.cleaned_data.get('card_expiry')
#             cvv = form.cleaned_data.get('cvv')

#             # Fetch items from cart (you may need to adjust based on your implementation)
#             cart_items = Cart.objects.filter(user=request.user)

#             # Create an order for each cart item
#             for item in cart_items:
#                 Order.objects.create(
#                     brand=item.brand,
#                     customer_name=customer_name,
#                     customer_email=customer_email,
#                     customer_address=customer_address,
#                     phone=phone,
#                     quantity=item.quantity,
#                     total_price=item.brand.price * item.quantity,
#                     payment_method=payment_method,
#                     card_number=card_number if payment_method == 'credit-card' else None,
#                     card_expiry=card_expiry if payment_method == 'credit-card' else None,
#                     cvv=cvv if payment_method == 'credit-card' else None,
#                 )

#             # Clear the cart after placing the order
#             cart_items.delete()

#             return render(request, 'checkout_success.html', {'customer_name': customer_name})
#     else:
#         form = CheckoutForm()

#     return render(request, "checkout.html", {'form': form})


# views.py


def my_orders(request):
    # Fetch all orders from the database
    categories = Category.objects.all()
    orderss = Order.objects.all()
    orders = Order.objects.all().values("ordered_at", "total_price")

    # Convert queryset to DataFrame
    data = pd.DataFrame(list(orders))

    if data.empty:
        return render(request, "myorder.html", {"sales_plot": None})

    # Ensure 'ordered_at' is a datetime type
    data["ordered_at"] = pd.to_datetime(data["ordered_at"], errors="coerce")

    # Convert `total_price` to numeric
    data["total_price"] = pd.to_numeric(data["total_price"], errors="coerce")

    # Drop rows where `total_price` is NaN
    data = data.dropna(subset=["total_price"])

    # Group orders by month
    data["ordered_at"] = data["ordered_at"].dt.tz_localize(None)
    data["month"] = data["ordered_at"].dt.to_period("M")
    sales_trend = data.groupby("month")["total_price"].sum()

    # Only generate the plot if there's more than one unique time point
    plot_url = None
    if len(sales_trend) > 1:
        plt.figure(figsize=(10, 5))
        sales_trend.plot(kind="line", marker="o", color="b")
        plt.title("Sales Trend Over Time")
        plt.xlabel("Month")
        plt.ylabel("Total Sales($)")
        plt.grid()

        # Convert plot to base64 string
        buffer = io.BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        string = base64.b64encode(buffer.read()).decode("utf-8")
        buffer.close()
        plot_url = f"data:image/png;base64,{string}"

    # Fraud Detection using Isolation Forest
    model = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)
    if not data.empty and "total_price" in data:
        data["anomaly"] = model.fit_predict(data[["total_price"]])
        fraud_orders = data[data["anomaly"] == -1]
    else:
        fraud_orders = None

    context = {
        "categories": categories,
        "orders": orders,
        "orderss": orderss,
        "sales_plot": plot_url,
        "fraud_orders": (
            fraud_orders.to_dict("records") if fraud_orders is not None else None
        ),
    }
    return render(request, "myorder.html", context)


def smart_search(query):
    vectorizer = TfidfVectorizer(stop_words="english")
    product_data = Brand.objects.all().values_list(
        "description", flat=True
    )  # Adjust as needed to get all product descriptions
    search_query = vectorizer.fit_transform([query] + list(product_data))
    similarity = cosine_similarity(search_query[0:1], search_query[1:])
    ranked_products = np.argsort(similarity[0])[
        ::-1
    ]  # Sort the products by similarity (descending order)
    return ranked_products


@login_required(login_url="/login/")
def myprofile(request):
    categories = Category.objects.all()
    user = request.user  # Get the currently logged-in user

    # Handle profile update when the form is submitted
    if request.method == "POST":
        first_name = (
            request.POST.get("first_name") or user.first_name
        )  # Default to current value if empty
        last_name = (
            request.POST.get("last_name") or user.last_name
        )  # Default to current value if empty
        username = (
            request.POST.get("username") or user.username
        )  # Default to current value if empty
        email = (
            request.POST.get("email") or user.email
        )  # Default to current value if empty
        password = request.POST.get("password")

        # Update the user fields
        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.email = email

        # Optionally handle password change if provided
        if password:
            user.set_password(password)

        # Save the updated user object
        user.save()

        # Optionally, you can display a success message
        messages.success(request, "Profile updated successfully!")

        # Handle customer details update (assuming customer details are stored in the Order model)
        customer_id = request.POST.get("customer_id")
        if customer_id:
            customer = Order.objects.get(
                id=customer_id
            )  # Assuming Order model holds customer details
            customer.customer_name = request.POST.get("customer_name")
            customer.customer_email = request.POST.get("customer_email")
            customer.customer_address = request.POST.get("customer_address")
            customer.phone = request.POST.get("customer_phone")
            customer.save()
            messages.success(request, "Customer details updated successfully!")

        return redirect("myprofile")  # Redirect to the same page after update

    # Retrieve the user's orders and customer details
    myprofile = Order.objects.all()  # Adjust based on your model relationships

    context = {
        "user": user,
        "myprofile": myprofile,  # Pass customer details to the template
        "categories": categories,
    }

    return render(request, "myprofile.html", context)
