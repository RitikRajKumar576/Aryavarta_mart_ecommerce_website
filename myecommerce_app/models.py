from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from datetime import date
from django.utils.timezone import now
from django.contrib.auth.hashers import make_password

# Create your models here.


class Brand(models.Model):
    CATEGORY_CHOICES = [
        ("mobiles", "Mobiles"),
        ("tablet", "Tablet"),
        ("tv", "TV"),
        ("laptop", "Laptop"),
        ("smartwatch", "Smartwatch"),
        ("accessory", "Accessory"),
    ]

    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    image = models.ImageField(upload_to="images/")
    category = models.CharField(
        max_length=50, choices=CATEGORY_CHOICES, default="mobiles"
    )  # Set default value
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Product_Cards(models.Model):
    heading = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to="images/")
    price = models.DecimalField(
        max_digits=10, decimal_places=2
    )  # ForeignKey to Brand model
    status = models.BooleanField(default=True)

    def formatted_price(self):
        """Returns the price formatted with commas."""
        return f"{self.price:,.2f}"

    def __str__(self):
        return self.heading


class Slideshow(models.Model):
    title = models.CharField(
        max_length=100, help_text="Title of the image", default="Default title"
    )
    caption = models.CharField(
        max_length=255, help_text="Caption for the image", default="Default caption"
    )
    image = models.ImageField(upload_to="images/")
    order = models.PositiveIntegerField(
        default=0, help_text="Order in which the image should appear"
    )

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title


class BrandOffer(models.Model):
    brand = models.CharField(max_length=100, help_text="Title of the brand")
    discount = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Discount percentage or offer"
    )
    description = models.TextField(help_text="Description of the offer")
    image = models.ImageField(upload_to="images/")

    def __str__(self):
        return self.brand


class Order(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Shipped", "Shipped"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
    ]

    PAYMENT_METHOD_CHOICES = [
        ("credit-card", "Credit Card"),
        ("upi", "UPI"),
        ("cash-on-delivery", "Cash on Delivery"),
    ]

    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    customer_address = models.TextField()
    phone = models.CharField(max_length=15, default="Not Provided")
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    ordered_at = models.DateTimeField(auto_now_add=True)

    # Payment Details
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHOD_CHOICES, default="cash-on-delivery"
    )
    card_number = models.CharField(max_length=16, null=True, blank=True)
    card_expiry = models.CharField(max_length=5, null=True, blank=True)  # MM/YY format
    cvv = models.CharField(max_length=4, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.total_price = self.brand.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.id} - {self.brand.name} ({self.status})"


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, blank=True, null=True)  # Allow blank slug

    def save(self, *args, **kwargs):
        if not self.slug:  # Generate slug only if it's not set
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Comingsoon(models.Model):
    header = models.CharField(max_length=255)
    name = models.CharField(max_length=100, default="Coming Soon Item")
    image = models.ImageField(upload_to="images/commingsoon/")
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0
    )  # ForeignKey to Brand model
    release_date = models.DateField(default=date.today)
    status = models.BooleanField(default=True)

    def formatted_price(self):
        """Returns the price formatted with commas."""
        return f"{self.price:,.2f}"

    def __str__(self):
        return self.header


class Dashboard_profile(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
    ]

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # Store hashed password
    created_at = models.DateTimeField(default=now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")

    def set_password(self, raw_password):
        """Hashes and sets the password."""
        self.password = make_password(raw_password)

    def __str__(self):
        return self.username


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Brand, on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
    
    
class Wishlist_product(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    products = models.ManyToManyField("Brand")
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Wishlist"
    
    
    




class Contact(models.Model):
    country = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.country


class State(models.Model):
    country = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="states")
    state = models.CharField(max_length=100)

    def __str__(self):
        return self.state


class ContactUs(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    country_name = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="contact_country")
    state_name = models.ForeignKey(State, on_delete=models.CASCADE, related_name="contact_state")
    message = models.TextField()
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"