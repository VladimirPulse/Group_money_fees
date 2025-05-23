import base64
from io import BytesIO

from PIL import Image

URL_ADMIN = "/admin/"
URL_CREAT_USER = "/auth/users/"
URL_TOKEN = "/auth/jwt/create/"
URL_COLLECT = "/api/collects/"
URL_PAY = "/api/payments/"
DEFAULT_SLUG = "birthday"

'''Создаем константу тестового изображения'''
image = Image.new("RGB", (1, 1), color="white")
buffered = BytesIO()
image.save(buffered, format="JPEG")
img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
IMAGE = "data:image/jpeg;base64," + f"{img_str}"
