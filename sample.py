@login_required(login_url='/login/')
def myprofile(request):
    user = request.user  # Get the currently logged-in user
    
    # Handle profile update when the form is submitted
    if request.method == "POST":
        first_name = request.POST.get('first_name') or user.first_name  # Default to current value if empty
        last_name = request.POST.get('last_name') or user.last_name  # Default to current value if empty
        username = request.POST.get('username') or user.username  # Default to current value if empty
        email = request.POST.get('email') or user.email  # Default to current value if empty
        password = request.POST.get('password')

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
        messages.success(request, 'Profile updated successfully!')
        
        # Handle customer details update (assuming customer details are stored in the Order model)
        customer_id = request.POST.get('customer_id')
        if customer_id:
            customer = Order.objects.get(id=customer_id)  # Assuming Order model holds customer details
            customer.customer_name = request.POST.get('customer_name')
            customer.customer_email = request.POST.get('customer_email')
            customer.customer_address = request.POST.get('customer_address')
            customer.phone = request.POST.get('customer_phone')
            customer.save()
            messages.success(request, 'Customer details updated successfully!')
        
        return redirect('myprofile')  # Redirect to the same page after update

    # Retrieve the user's orders and customer details
    myprofile = Order.objects.all()  # Adjust based on your model relationships

    context = {
        'user': user,
        'myprofile': myprofile  # Pass customer details to the template
    }

    return render(request, "myprofile.html", context)