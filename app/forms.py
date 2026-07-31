from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from django import forms

from .models import (
    ProductVariant,
    VariantSpecification,
    Specification,
)
class RegisterForm(UserCreationForm):

    first_name = forms.CharField(max_length=50)

    last_name = forms.CharField(max_length=50)

    email = forms.EmailField()

    class Meta:

        model = User

        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "password1",
            "password2",
        )

from django import forms

from .models import *
from django import forms
from .models import Product


class ProductForm(forms.ModelForm):

    vat_inclusive = forms.BooleanField(
        required=False,
        initial=True,
        label="Price Includes VAT",
        help_text=(
            "✓ Checked: The entered price already includes 16% VAT.<br>"
            "✗ Unchecked: The entered price excludes VAT."
        ),
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input form-switch",
            }
        ),
    )

    class Meta:

        model = Product

        fields = [
            "name",
            "slug",
            "category",
            "brand",
            "image",
            "short_description",
            "description",
            "condition",
            "warranty",
            "vat_inclusive",
            "featured",
            "new_arrival",
            "trending",
            "active",
        ]

        widgets = {

            "name": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "slug": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "category": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "brand": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "image": forms.ClearableFileInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "short_description": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 6
                }
            ),

            "condition": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "warranty": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "featured": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),

            "new_arrival": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),

            "trending": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),

            "active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),

        }

from django import forms
from .models import Category


class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = [
            "name",
            "slug",
            "description",
            "icon",
        ]

        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
        }

from django import forms
from .models import Brand


class BrandForm(forms.ModelForm):

    class Meta:
        model = Brand

        fields = [
            "name",
            "logo",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter brand name"
                }
            ),

            "logo": forms.ClearableFileInput(
                attrs={
                    "class": "form-control"
                }
            ),
        }

    def clean_name(self):
        name = self.cleaned_data["name"]

        return name.strip()
from django import forms
from django import forms
from .models import Order


class OrderForm(forms.ModelForm):

    class Meta:
        model = Order

        fields = [
            "full_name",
            "email",
            "phone",
            "address",
            "city",
            "county",
            "postcode",
            "notes",
            "payment_method",
            "delivery_method",
            "vat_option",
            "subtotal",
            "delivery_fee",
            "vat_amount",
            "grand_total",
        ]

        widgets = {

            "full_name": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "email": forms.EmailInput(attrs={
                "class": "form-control"
            }),

            "phone": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "address": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3
            }),

            "city": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "county": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "postcode": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "notes": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3
            }),

            "payment_method": forms.Select(attrs={
                "class": "form-select"
            }),

            "delivery_method": forms.Select(attrs={
                "class": "form-select"
            }),

            "vat_option": forms.Select(attrs={
                "class": "form-select"
            }),

            "subtotal": forms.NumberInput(attrs={
                "class": "form-control"
            }),

            "delivery_fee": forms.NumberInput(attrs={
                "class": "form-control"
            }),

            "vat_amount": forms.NumberInput(attrs={
                "class": "form-control"
            }),

            "grand_total": forms.NumberInput(attrs={
                "class": "form-control"
            }),

        }
from django import forms


from django import forms


class ProductImportForm(forms.Form):

    urls = forms.CharField(

        label="Product URLs",

        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 10,
                "placeholder": (
                    "Paste one product URL per line.\n\n"
                    "Example:\n"
                    "https://...\n"
                    "https://...\n"
                    "https://..."
                ),
            }
        ),
    )

    def clean_urls(self):
        text = self.cleaned_data["urls"]

        urls = [
            url.strip()
            for url in text.splitlines()
            if url.strip()
        ]

        if not urls:
            raise forms.ValidationError("Please provide at least one product URL.")

        if len(urls) > 10:
            raise forms.ValidationError("You can import a maximum of 10 products at once.")

        return urls
from django import forms
from .models import VariantSpecification, Specification


class VariantSpecificationForm(forms.ModelForm):

    class Meta:
        model = VariantSpecification
        fields = [
            "specification",
            "value",
        ]

        widgets = {

            "specification": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "value": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Value"
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        category = kwargs.pop("category", None)

        super().__init__(*args, **kwargs)

        if category:

            self.fields["specification"].queryset = (
                Specification.objects.filter(
                    category=category
                )
            )

        else:

            self.fields["specification"].queryset = (
                Specification.objects.none()
            )
from django.forms import BaseInlineFormSet
from django.forms import inlineformset_factory


class BaseVariantSpecificationFormSet(BaseInlineFormSet):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        category = None

        if self.instance.pk:

            category = self.instance.product.category

        for form in self.forms:

            form.fields["specification"].queryset = (
                Specification.objects.filter(
                    category=category
                )
            )


VariantSpecificationFormSet = inlineformset_factory(

    ProductVariant,

    VariantSpecification,

    form=VariantSpecificationForm,

    formset=BaseVariantSpecificationFormSet,

    extra=6,

    can_delete=True,
)
from django import forms

from .models import ProductVariant


class ProductVariantForm(forms.ModelForm):

    class Meta:
        model = ProductVariant

        fields = [
            "price",
            "discount_price",
            "stock",
            "sku",
            "image",
            "discount_start",
            "discount_end",
            "active",
        ]

        widgets = {

            "price": forms.NumberInput(attrs={
                "class": "form-control"
            }),

            "discount_price": forms.NumberInput(attrs={
                "class": "form-control"
            }),

            "stock": forms.NumberInput(attrs={
                "class": "form-control"
            }),

            "sku": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "image": forms.ClearableFileInput(attrs={
                "class": "form-control"
            }),

            "discount_start": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),

            "discount_end": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),

            "active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),
        }


from django import forms
from .models import Banner


class BannerForm(forms.ModelForm):

    class Meta:
        model = Banner
        category = forms.ModelChoiceField(
    queryset=Category.objects.all(),
    required=False
)

        fields = [
            "title",
            "subtitle",
            "image",
            "banner_type",
            "category",
            "brand",
            "button_text",
            "button_link",
            "background_color",
            "text_color",
            "order",
            "active",
            "start_date",
            "end_date",
        ]

        widgets = {

            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Banner title"
            }),

            "subtitle": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Banner subtitle"
            }),

            "banner_type": forms.Select(attrs={
                "class": "form-select"
            }),

            "category": forms.Select(attrs={
                "class": "form-select"
            }),

            "brand": forms.Select(attrs={
                "class": "form-select"
            }),

            "button_text": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "button_link": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "background_color": forms.TextInput(attrs={
                "type": "color",
                "class": "form-control form-control-color"
            }),

            "text_color": forms.TextInput(attrs={
                "type": "color",
                "class": "form-control form-control-color"
            }),

            "order": forms.NumberInput(attrs={
                "class": "form-control"
            }),

            "start_date": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "form-control"
                }
            ),

            "end_date": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "form-control"
                }
            ),

            "active": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),

        }

from django import forms
from .models import DealCampaign


from django import forms
from .models import DealCampaign, ProductVariant


class DealCampaignForm(forms.ModelForm):

    products = forms.ModelMultipleChoiceField(
        queryset=ProductVariant.objects.select_related(
            "product"
        ).all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:

        model = DealCampaign

        fields = (
            "name",
            "description",
            "holder_image",
            "banner",
            "products",
            "discount_type",
            "discount_value",
            "start_date",
            "end_date",
            "active",
        )

        widgets = {

            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Campaign Name"
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4
                }
            ),

            "discount_type": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "discount_value": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01"
                }
            ),

            "start_date": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "form-control"
                }
            ),

            "end_date": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "form-control"
                }
            ),

            "active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),

        }

from django import forms
from .models import MarketingCampaign


class MarketingCampaignForm(forms.ModelForm):

    class Meta:

        model = MarketingCampaign

        fields = [

            "title",
            "subject",
            "message",
            "products",

        ]

        widgets = {

            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "July Laptop Promotion",
                }
            ),

            "subject": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "🔥 Huge Price Drop on Top Products!",
                }
            ),

            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 6,
                    "placeholder": "Optional custom message...",
                }
            ),

            "products": forms.CheckboxSelectMultiple(),

        }

from django import forms

from .models import InventoryTransaction


class StockInForm(forms.ModelForm):

    class Meta:
        model = InventoryTransaction

        fields = [
            "quantity",
            "reference",
            "notes",
        ]

        widgets = {
            "quantity": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                }
            ),

            "reference": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),
        }


class StockOutForm(forms.ModelForm):

    class Meta:
        model = InventoryTransaction

        fields = [
            "quantity",
            "reference",
            "notes",
        ]

        widgets = {
            "quantity": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                }
            ),

            "reference": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),
        }


class StockAdjustmentForm(forms.ModelForm):

    class Meta:
        model = InventoryTransaction

        fields = [
            "quantity",
            "reference",
            "notes",
        ]

        widgets = {
            "quantity": forms.NumberInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "reference": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),
        }
from django import forms
from app.models import InventoryTransaction, ProductVariant


class InventoryTransactionForm(forms.ModelForm):

    class Meta:
        model = InventoryTransaction

        fields = [
            "variant",
            "transaction_type",
            "quantity",
            "reference",
            "notes",
        ]

        widgets = {
            "variant": forms.Select(attrs={
                "class": "form-select"
            }),

            "transaction_type": forms.Select(attrs={
                "class": "form-select"
            }),

            "quantity": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
            }),

            "reference": forms.TextInput(attrs={
                "class": "form-control",
            }),

            "notes": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
            }),
        }
from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget
class BlogForm(forms.ModelForm):

    class Meta:

        model = BlogPost

        fields = "__all__"

        widgets = {

            "content": CKEditor5Widget(

                config_name="default"

            )

        }

from django import forms


class QuoteRequestForm(forms.Form):
    company_name = forms.CharField(max_length=200)
    contact_person = forms.CharField(max_length=150)

    email = forms.EmailField()

    phone = forms.CharField(max_length=30)

    whatsapp = forms.CharField(
        max_length=30,
        required=False
    )

    kra_pin = forms.CharField(
        max_length=30,
        required=False
    )

    address = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3})
    )

    city = forms.CharField(max_length=100)

    BILLING = (
        ("inclusive", "VAT Inclusive"),
        ("exclusive", "VAT Exclusive"),
    )

    billing_type = forms.ChoiceField(
        choices=BILLING,
        widget=forms.RadioSelect
    )

    notes = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 5}),
        required=False
    )

from django import forms
from .models import NewsletterSubscriber


class NewsletterSubscriberForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ["email"]

        widgets = {
            "email": forms.EmailInput(
                attrs={
                    "placeholder": "Enter your email address",
                    "class": "newsletter-input",
                }
            )
        }

    def clean_email(self):
        email = self.cleaned_data["email"].lower().strip()

        if NewsletterSubscriber.objects.filter(
            email=email,
            active=True
        ).exists():
            raise forms.ValidationError(
                "You are already subscribed."
            )

        return email

from .models import Deal


class DealForm(forms.ModelForm):

    class Meta:

        model = Deal

        fields = [
            "product",
            "old_price",
            "new_price",
            "discount_start",
            "discount_end",
            "active",
        ]


        widgets = {

            "discount_start":
            forms.DateTimeInput(
                attrs={
                    "type":"datetime-local",
                    "class":"form-control"
                }
            ),


            "discount_end":
            forms.DateTimeInput(
                attrs={
                    "type":"datetime-local",
                    "class":"form-control"
                }
            ),

        }