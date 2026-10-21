
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "https://www.saucedemo.com/"
USERNAME = "standard_user"
PASSWORD = "secret_sauce"



@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()

    options.add_argument("--incognito")
    options.add_argument("--disable-save-password-bubble")

    browser = webdriver.Chrome(options=options)
    browser.maximize_window()
    browser.get(BASE_URL)

    yield browser

    browser.quit()


def login(driver, username=USERNAME, password=PASSWORD):
    driver.find_element(By.ID, "user-name").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "login-button").click()


def test_TC01_login_success(driver):
    login(driver)

    products = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.CLASS_NAME, "inventory_list")
        )
    )

    assert products.is_displayed()


def test_TC02_login_wrong_password(driver):
    login(driver, USERNAME, "wrong_password")

    error = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "[data-test='error']")
        )
    )

    assert "Username and password do not match" in error.text


def test_TC03_locked_user(driver):
    login(driver, "locked_out_user", PASSWORD)

    error = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "[data-test='error']")
        )
    )

    assert "locked out" in error.text.lower()


def test_TC04_add_product_to_cart(driver):
    login(driver)

    driver.find_element(
        By.ID, "add-to-cart-sauce-labs-backpack"
    ).click()

    badge = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.CLASS_NAME, "shopping_cart_badge")
        )
    )

    assert badge.text == "1"


def test_TC05_remove_product_from_cart(driver):
    login(driver)

    driver.find_element(
        By.ID, "add-to-cart-sauce-labs-backpack"
    ).click()

    driver.find_element(
        By.CLASS_NAME, "shopping_cart_link"
    ).click()

    driver.find_element(
        By.ID, "remove-sauce-labs-backpack"
    ).click()

    assert len(
        driver.find_elements(By.CLASS_NAME, "cart_item")
    ) == 0


def test_TC06_sort_price_low_to_high(driver):
    login(driver)

    dropdown = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.CLASS_NAME, "product_sort_container")
        )
    )

    Select(dropdown).select_by_value("lohi")

    prices = WebDriverWait(driver, 10).until(
        EC.visibility_of_all_elements_located(
            (By.CLASS_NAME, "inventory_item_price")
        )
    )

    values = [
        float(price.text.replace("$", ""))
        for price in prices
    ]

    assert values == sorted(values)




# TC07: Đăng xuất
def test_TC07_logout(driver):
    login(driver)

    wait = WebDriverWait(driver, 10)

    # Xác nhận đăng nhập thành công trước khi đăng xuất
    wait.until(
        EC.visibility_of_element_located(
            (By.CLASS_NAME, "inventory_list")
        )
    )

    # Mở menu
    wait.until(
        EC.element_to_be_clickable(
            (By.ID, "react-burger-menu-btn")
        )
    ).click()

    # Nhấn Logout
    wait.until(
        EC.element_to_be_clickable(
            (By.ID, "logout_sidebar_link")
        )
    ).click()

    # Chờ nút đăng nhập xuất hiện, không phụ thuộc URL chính xác
    try:
        login_button = wait.until(
            EC.visibility_of_element_located(
                (By.ID, "login-button")
            )
        )
    except Exception:
        print("URL sau Logout:", driver.current_url)
        print("Title sau Logout:", driver.title)
        raise

    assert login_button.is_displayed()
    assert driver.find_element(By.ID, "user-name").is_displayed()
    assert driver.find_element(By.ID, "password").is_displayed()