import logging
from homeassistant.helpers.entity import Entity
from .naver_land import NaverLandApi
from .const import DOMAIN, CONF_EXCLUDE_LOW_FLOORS, CONF_LOW_FLOOR_LIMIT

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Naver Land sensors from a config entry."""
    # config_entry에서 필요한 설정 값 추출
    apt_id = config_entry.data["username"]
    area = config_entry.data["variables"]
    exclude_low_floors = config_entry.options.get(CONF_EXCLUDE_LOW_FLOORS, False)
    low_floor_limit = config_entry.options.get(CONF_LOW_FLOOR_LIMIT, 5)

    # 센서 엔티티 추가
    async_add_entities([
        NaverLandMaxPriceSensor(apt_id, area, exclude_low_floors, low_floor_limit),
        NaverLandMinPriceSensor(apt_id, area, exclude_low_floors, low_floor_limit),
        NaverLandPriceDistributionSensor(apt_id, area, exclude_low_floors, low_floor_limit),
    ], False)


def convert_price_to_float(price_str):
    """Convert price string (e.g., '5억 3000' or '2억') to float."""
    try:
        parts = price_str.replace(',', '').split('억')
        if len(parts) == 2:
            return float(parts[0]) + (float(parts[1]) / 10000 if parts[1] else 0)
        elif len(parts) == 1:
            return float(parts[0]) / 10000
        return 0.0
    except ValueError:
        return 0.0


class NaverLandMaxPriceSensor(Entity):
    """Sensor for the maximum price of a property."""

    def __init__(self, apt_id, area, exclude_low_floors=False, low_floor_limit=5):
        self.api = NaverLandApi(
            apt_id=apt_id,
            area=area,
            exclude_low_floors=exclude_low_floors,
            low_floor_limit=low_floor_limit,
        )
        self._name = f"{apt_id}-max-price"
        self._data = None
        self._value = None

    async def async_added_to_hass(self):
        """Initialize the sensor when added to Home Assistant."""
        await self.async_update()

    async def async_update(self):
        """Fetch data and update state."""
        articles = await self.api.get_all_articles()
        if articles:
            max_price_article = max(articles, key=lambda x: convert_price_to_float(x.dealOrWarrantPrc))
            self._data = max_price_article.__dict__
            self._value = convert_price_to_float(max_price_article.dealOrWarrantPrc)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the current state of the sensor."""
        return self._value

    @property
    def extra_state_attributes(self):
        """Return the additional attributes of the sensor."""
        return self._data


class NaverLandMinPriceSensor(Entity):
    """Sensor for the minimum price of a property."""

    def __init__(self, apt_id, area, exclude_low_floors=False, low_floor_limit=5):
        self.api = NaverLandApi(
            apt_id=apt_id,
            area=area,
            exclude_low_floors=exclude_low_floors,
            low_floor_limit=low_floor_limit,
        )
        self._name = f"{apt_id}-min-price"
        self._data = None
        self._value = None

    async def async_added_to_hass(self):
        """Initialize the sensor when added to Home Assistant."""
        await self.async_update()

    async def async_update(self):
        """Fetch data and update state."""
        articles = await self.api.get_all_articles()
        if articles:
            min_price_article = min(articles, key=lambda x: convert_price_to_float(x.dealOrWarrantPrc))
            self._data = min_price_article.__dict__
            self._value = convert_price_to_float(min_price_article.dealOrWarrantPrc)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the current state of the sensor."""
        return self._value

    @property
    def extra_state_attributes(self):
        """Return the additional attributes of the sensor."""
        return self._data


class NaverLandPriceDistributionSensor(Entity):
    """Sensor for the price distribution of properties."""

    def __init__(self, apt_id, area, exclude_low_floors=False, low_floor_limit=5):
        self.api = NaverLandApi(
            apt_id=apt_id,
            area=area,
            exclude_low_floors=exclude_low_floors,
            low_floor_limit=low_floor_limit,
        )
        self._name = f"{apt_id}-price-distribution"
        self._data = {}
        self._value = None

    async def async_added_to_hass(self):
        """Initialize the sensor when added to Home Assistant."""
        await self.async_update()

    async def async_update(self):
        """Fetch data and update state."""
        articles = await self.api.get_all_articles()
        if articles:
            price_distribution = {}
            for article in articles:
                price = convert_price_to_float(article.dealOrWarrantPrc)
                confirm_date = article.articleConfirmYmd
                if confirm_date not in price_distribution:
                    price_distribution[confirm_date] = []
                price_distribution[confirm_date].append(price)

            self._data = price_distribution
            self._value = sum(len(prices) for prices in price_distribution.values())

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the total number of price entries."""
        return self._value

    @property
    def extra_state_attributes(self):
        """Return the price distribution as additional attributes."""
        return self._data
