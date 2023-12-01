from rest_framework.pagination import PageNumberPagination


class MyPaginator(PageNumberPagination):
    """
    Кастомный класс для пагинации для привычек
    """

    page_size = 5  # Количество элементов на странице
    page_size_query_param = 'page_size'  # Параметр запроса для указания количества элементов на странице
    max_page_size = 50  # Максимальное количество элементов на странице
