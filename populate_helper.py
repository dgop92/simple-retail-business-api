import os
import random

import django
from django.urls import reverse

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", 
    "simple_retail_business_api.settings"
)
django.setup()

from account.models import MyUser
from account.tests.mixins import TestAccountBase, TestsMixin
from account.urls import login_view_name
from dashboard.models import Brand, Catalogue, Product, Provider
from dashboard.tests.data_generator import (BasicDashboardtUrlDataGetter,
                                            CoreDashboardtUrlDataGetter)


class UserPopulator(TestAccountBase):

    def __init__(self):
        self.init()
        self.init_account_data_url()

    def start(self, superuser_data):

        self.superuser_token = \
            self.login_user_with_credentials_and_get_token(superuser_data)

        self.populate_users()
        self.populate_profiles()

    def populate_users(self):

        # Register admin
        self.register_new_user(register_data = self.ADMIN_DATA)

        # Register Employees
        self.employee1_data = self.get_random_new_user_data()
        self.employee2_data = self.get_random_new_user_data()
        self.register_new_user(register_data = self.employee1_data)
        self.register_new_user(register_data = self.employee2_data)

    def populate_profiles(self):

        auth_datas = [
            {
                "username": self.ADMIN_DATA['username'],
                "password": self.ADMIN_DATA['password']
            },
            {
                "username": self.employee1_data['username'],
                "password": self.employee1_data['password'],
            },
            {
                "username": self.employee2_data['username'],
                "password": self.employee2_data['password'],
            }
        ]

        for auth_data in auth_datas:
            token = self.login_user_with_credentials_and_get_token(auth_data)

            self.put(
                self.profile_url,
                data = self.get_random_profile_data(),
                token = token
            )

    # Override
    def register_new_user(self, register_data):
        self.post(
            self.register_view, 
            data = register_data, 
            token = self.superuser_token
        )
    

class BasicPopulator(TestsMixin, BasicDashboardtUrlDataGetter):

    AMOUNT_OF_BRANDS_CATALOGUES = 10
    AMOUNT_OF_PRODUCTS = 50
    AMOUNT_OF_PROVIDERS = 5

    def __init__(self):
        self.init()
        self.init_basic_dashboard_url_data()
    
    def start(self):

        self.post(
            reverse(login_view_name),
            data = {
                "username": "admin_dp",
                "password": "admin1234admin"
            }
        )

        self.admin_token = self.json_response['key']

        self.create_catalogue_brands()
        self.create_products()
        self.create_providers()
            
    def create_catalogue_brands(self):

        for _ in range(self.AMOUNT_OF_BRANDS_CATALOGUES):

            self.post(
                self.get_brand_url(),
                data = self.get_brand_valid_data(),
                token = self.admin_token
            )

            self.post(
                self.get_catalogue_url(),
                data = self.get_catalogue_valid_data(),
                token = self.admin_token
            )

    def create_products(self):

        brands = Brand.objects.all()
        catalogues = Catalogue.objects.all()

        for _ in range(self.AMOUNT_OF_PRODUCTS):

            random_brand = random.choice(brands)
            random_catalogue = random.choice(catalogues)

            self.post(
                self.get_product_url(),
                data = self.get_product_valid_data(
                    random_brand.name,
                    random_catalogue.name,
                ),
                token = self.admin_token
            )

    def create_providers(self):

        for _ in range(self.AMOUNT_OF_PROVIDERS):

            self.post(
                self.get_provider_url(),
                data = self.get_provider_valid_data(),
                token = self.admin_token
            )

class CorePopulator(TestsMixin, CoreDashboardtUrlDataGetter):

    AMOUNT_OF_ENTRIES = 5
    AMOUNT_OF_PURCHASES = 100

    AMOUNT_OF_EXITS = 80
    
    def __init__(self):
        self.init()
        self.init_core_dashboard_url_data()
    
    def start(self):

        self.tokens = []

        users = MyUser.objects.all()
        login_url = reverse(login_view_name)

        for user in users:
            self.post(
                login_url,
                data = {
                    "username": user.username,
                    "password": "admin1234admin"
                }
            )
            self.tokens.append(self.json_response['key'])

        self.create_entries_purchases()
        self.create_exits_sales()
    
    def create_entries_purchases(self):

        providers = Provider.objects.all()
        products = Product.objects.all()

        for _ in range(self.AMOUNT_OF_ENTRIES):
            print("Creating new entry...")

            random_provider = random.choice(providers)
            random_token = random.choice(self.tokens)
            
            self.post(
                self.get_entry_url(),
                data = self.get_entry_valid_data(random_provider.name),
                token = random_token
            )

            entry_id = self.json_response['pk']
        
            for _ in range(self.AMOUNT_OF_PURCHASES):

                random_product = random.choice(products)

                self.post(
                    self.get_purchase_url(),
                    data = self.get_purchase_valid_data(
                        entry_id,
                        random_product.code
                    ),
                    token = random_token
                )


    def create_exits_sales(self):

        products = Product.objects.all()

        for _ in range(self.AMOUNT_OF_EXITS):
            print("Creating new exit...")

            random_token = random.choice(self.tokens)
            
            self.post(
                self.get_exit_url(),
                token = random_token
            )

            exit_id = self.json_response['pk']

            amount_of_sales = random.randint(1, 5)
        
            for _ in range(amount_of_sales):

                random_product = random.choice(products)

                self.post(
                    self.get_sale_url(),
                    data = self.get_sale_valid_data(
                        exit_id,
                        random_product.code
                    ),
                    token = random_token
                )


if __name__ == "__main__":
    
    """ users_populator = UserPopulator()
    users_populator.start({
        "username": "root",
        "password": "root1234"
    }) """

    """ basic_data_populator = BasicPopulator()
    basic_data_populator.start() """
    
    core_populator = CorePopulator()
    core_populator.print_output = False
    core_populator.start()


    
