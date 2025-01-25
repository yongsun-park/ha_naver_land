import asyncio
import logging
from homeassistant.helpers.entity import Entity
from .naver_land import NaverLandApi
from .const import DOMAIN, CONF_EXCLUDE_LOW_FLOORS, CONF_LOW_FLOOR_LIMIT

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the NaverLand sensors from a config entry."""
    data = config_entry.data
    options = config_entry.options

    async_add_entities([
        NaverLandMaxPriceSensor(data, options),
        NaverLandMinPriceSensor(data, options),
        NaverLandPriceDistributionSensor(data, options),
    ])


def convert_price_to_float(price_str):
    """Convert a price string to a float."""
    try:
        # Remove commas and split the string by '억'
        parts = price_str.replace(',', '').split('억')
        if len(parts) == 2:
            return float(parts[0]) + (float(parts[1]) / 10000 if parts[1] else 0)
        elif len(parts) == 1:
            return float(parts[0]) / 10000
        else:
            return 0.0
    except ValueError:
        return 0.0


class NaverLandSensorBase(Entity):
    """Base class for NaverLand sensors."""
    def __init__(self, data, options):
        self.apt_id = data["username"]
        self.area = data["variables"]
        self.exclude_low_floors = options.get(CONF_EXCLUDE_LOW_FLOORS, False)
        self.low_floor_limit = options.get(CONF_LOW_FLOOR_LIMIT, 5)
        self.api = None
        self._value = None
        self._data = None

    async def async_added_to_hass(self):
        """Initialize the API when the entity is added to Home Assistant."""
        self.api = NaverLandApi(
            apt_id=self.apt_id,
            area=self.area,
            exclude_low_floors=self.exclude_low_floors,
            low_floor_limit=self.low_floor_limit,
        )
        await self.async_update()

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._value

    @property
    def extra_state_attributes(self):
        """Return additional attributes of the sensor."""
        return self._data


class NaverLandMaxPriceSensor(NaverLandSensorBase):
    """Sensor to get the maximum price from NaverLand."""

    def __init__(self, data, options):
        super().__init__(data, options)
        self._name = f"{self.apt_id}-max-price"

    async def async_update(self):
        """Fetch the maximum price and update the state."""
        if not self.api:
            return

        articles = await self.api.get_all_articles()
        if articles:
            max_price_article = max(articles, key=lambda x: convert_price_to_float(x.dealOrWarrantPrc))
            self._value = convert_price_to_float(max_price_article.dealOrWarrantPrc)
            self._data = max_price_article.__dict__

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name


class NaverLandMinPriceSensor(NaverLandSensorBase):
    """Sensor to get the minimum price from NaverLand."""

    def __init__(self, data, options):
        super().__init__(data, options)
        self._name = f"{self.apt_id}-min-price"

    async def async_update(self):
        """Fetch the minimum price and update the state."""
        if not self.api:
            return

        articles = await self.api.get_all_articles()
        if articles:
            min_price_article = min(articles, key=lambda x: convert_price_to_float(x.dealOrWarrantPrc))
            self._value = convert_price_to_float(min_price_article.dealOrWarrantPrc)
            self._data = min_price_article.__dict__

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name


class NaverLandPriceDistributionSensor(NaverLandSensorBase):
    """Sensor to get the price distribution from NaverLand."""

    def __init__(self, data, options):
        super().__init__(data, options)
        self._name = f"{self.apt_id}-price-distribution"
        self._distribution = {}

    async def async_update(self):
        """Fetch price distribution and update the state."""
        if not self.api:
            return

        articles = await self.api.get_all_articles()
        if articles:
            distribution = {}
            for article in articles:
                price = convert_price_to_float(article.dealOrWarrantPrc)
                distribution.setdefault(price, 0)
                distribution[price] += 1

            self._distribution = distribution
            self._value = len(distribution)

    @property
    def extra_state_attributes(self):
        """Return the price distribution as additional attributes."""
        return {"distribution": self._distribution}

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name
