from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Contact
from .forms import ContactForm, SignUpForm

def contact_list(request):
    if not request.user.is_authenticated:
        return redirect('login')

    query = request.GET.get('q')
    try:
        if query:
            contacts = Contact.objects.filter(
                Q(user=request.user) & (
                    Q(name__icontains=query) |
                    Q(phone__icontains=query) |
                    Q(email__icontains=query) |
                    Q(address__icontains=query)
                )
            )
        else:
            contacts = Contact.objects.filter(user=request.user)
    except Exception as e:
        messages.error(request, f"Error loading contacts: {e}")
        contacts = []

    paginator = Paginator(contacts, 5)  # Show 5 contacts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'contacts/contact_list.html', {'contacts': page_obj, 'query': query or ''})

@login_required
def contact_create(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            try:
                contact = form.save(commit=False)
                contact.user = request.user
                contact.save()
                messages.success(request, 'Contact created successfully.')
                return redirect('contact_list')
            except Exception as e:
                messages.error(request, f"Failed to create contact: {e}")
    else:
        form = ContactForm()
    return render(request, 'contacts/contact_form.html', {'form': form})

@login_required
def contact_update(request, pk):
    contact = get_object_or_404(Contact, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Contact updated successfully.')
                return redirect('contact_list')
            except Exception as e:
                messages.error(request, f"Failed to update contact: {e}")
    else:
        form = ContactForm(instance=contact)
    return render(request, 'contacts/contact_form.html', {'form': form})

@login_required
def contact_delete(request, pk):
    contact = get_object_or_404(Contact, pk=pk, user=request.user)
    if request.method == 'POST':
        try:
            contact.delete()
            messages.success(request, 'Contact deleted successfully.')
        except Exception as e:
            messages.error(request, f"Failed to delete contact: {e}")
        return redirect('contact_list')
    return render(request, 'contacts/contact_confirm_delete.html', {'contact': contact})

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        try:
            if form.is_valid():
                user = form.save()
                login(request, user)
                messages.success(request, 'Signup successful.')
                return redirect('contact_list')
        except Exception as e:
            messages.error(request, f"Signup failed: {e}")
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

