from ...sample import sample_service
from ...sample.sample_service import GroceryListItem
import pytest
import random

# test classes must be prepended with Test to be discovered by pytest
class TestClass:
    # each test name must start with test_ to be discovered by pytest

    # basic unit test example, learn about invoking pytest here: https://docs.pytest.org/en/7.2.x/how-to/usage.html
    def test_addTwo(self):
        # arrange
        service = sample_service.SampleNumberService()
        # act
        result = service.addTwo(1)
        # assert, learn more about asserts here: https://docs.pytest.org/en/7.2.x/how-to/assert.html
        assert result == 3

    # parameterized unit test example, learn more here: https://docs.pytest.org/en/7.2.x/how-to/parametrize.html
    @pytest.mark.parametrize("n,expected", [(1,3), (2,4), (-1,1)])
    def test_addTwo_parameterized(self, n, expected):
        # arrange
        service = sample_service.SampleNumberService()
        # act
        result = service.addTwo(n)
        # assert
        assert result == expected

    # fixture unit test example, learn more here: https://docs.pytest.org/en/7.2.x/how-to/fixtures.html
    # arrange
    @pytest.fixture
    def grocery_list_item(self):
        return GroceryListItem("dozen eggs", 2)
    
    def test_groceryListItem_purchased(self, grocery_list_item):
        # act
        grocery_list_item.purchase()        
        # assert
        assert grocery_list_item.purchased == True

    # mocking example, learn more here: https://docs.pytest.org/en/7.2.x/how-to/monkeypatch.html
    def test_addRandom(self):
        # arrange
        monkeypatch = pytest.MonkeyPatch()
        monkeypatch.setattr(random, "randrange", lambda a, b: 5)
        # act
        result = sample_service.SampleNumberService.addRandom(1)
        # assert
        assert result == 6