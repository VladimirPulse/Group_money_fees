# from pytils.translit import slugify

# from menu_app.models import Menu, MenuItem
# from menu_app.pytest_tests.constans import URL_ITEM_ADD, URL_MENU_ADD


# def test_creat_tree_menu(admin_client, form_data, form_data_2, form_data_3):
#     """Проверка на наличие древовидной иерархии"""
#     # Убедимся, что в БД пуста
#     assert MenuItem.objects.count() == 0
#     assert Menu.objects.count() == 0
#     admin_client.post(URL_MENU_ADD, data=form_data)
#     assert Menu.objects.count() == 1
#     new_menu = Menu.objects.get()
#     # Попробуем добавить подменю
#     admin_client.post(URL_ITEM_ADD, data=form_data_2)
#     assert MenuItem.objects.count() == 1
#     new_item_1 = MenuItem.objects.get()
#     assert new_menu.items.get().id == new_item_1.id
#     # Попробуем добавить пункт подменю
#     admin_client.post(URL_ITEM_ADD, data=form_data_3)
#     assert MenuItem.objects.count() == 2
#     # Извлечем именно созданный пункт и проверим,
#     # что это именно он
#     new_item_2 = MenuItem.objects.exclude(id=new_item_1.id).get()
#     assert new_item_1.children.get().id == new_item_2.id


# def test_not_unique_slug(admin_client, form_data, form_data_2, form_data_3):
#     """Проверка на уникальность named_url"""
#     assert MenuItem.objects.count() == 0
#     assert Menu.objects.count() == 0
#     admin_client.post(URL_MENU_ADD, data=form_data)
#     assert Menu.objects.count() == 1
#     admin_client.post(URL_ITEM_ADD, data=form_data_2)
#     assert MenuItem.objects.count() == 1
#     form_data_3["named_url"] = form_data_2["named_url"]
#     admin_client.post(URL_ITEM_ADD, data=form_data_3)
#     assert MenuItem.objects.count() == 1


# def test_empty_slug(admin_client, form_data, form_data_2):
#     """Проверка, что даже без named_url создается экземпляр модели"""
#     assert MenuItem.objects.count() == 0
#     assert Menu.objects.count() == 0
#     admin_client.post(URL_MENU_ADD, data=form_data)
#     assert Menu.objects.count() == 1
#     form_data_2.pop("named_url")
#     admin_client.post(URL_ITEM_ADD, data=form_data_2)
#     assert MenuItem.objects.count() == 1
#     new_item = MenuItem.objects.get()
#     expected_slug = slugify(form_data_2["title"])
#     assert new_item.named_url == expected_slug
