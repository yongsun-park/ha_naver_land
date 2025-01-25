from homeassistant.helpers.entity import Entity
from .naver_land import NaverLandApi
from .const import DOMAIN, CONF_EXCLUDE_LOW_FLOORS, CONF_LOW_FLOOR_LIMIT
import hashlib

def convert_price_to_float(price_str):
    try:
        # Remove commas and split the string by '억'
        parts = price_str.replace(',', '').split('억')
        if len(parts) == 2:
            # Convert the parts to float and calculate the final value
            return float(parts[0]) + (float(parts[1]) / 10000 if parts[1] else 0)
        elif len(parts) == 1:
            return float(parts[0]) / 10000
        else:
            return 0.0
    except ValueError:
        return 0.0

class NaverLandSensorBase(Entity):
    """Base class for NaverLand sensors."""
    def __init__(self, data, options, sensor_type):
        self.apt_id = data["username"]
        self.area = data["variables"]
        self.exclude_low_floors = options.get(CONF_EXCLUDE_LOW_FLOORS, False)
        self.low_floor_limit = options.get(CONF_LOW_FLOOR_LIMIT, 5)
        self.sensor_type = sensor_type
        self.api = None
        self._value = None
        self._data = None
        self._name = f"{self.apt_id}-{self.sensor_type}"
        # Generate a unique ID based on apt_id and sensor type
        self._unique_id = hashlib.md5(f"{self.apt_id}-{self.sensor_type}".encode()).hexdigest()

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
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def state(self):
        return self._value

    @property
    def extra_state_attributes(self):
        return self._data
    
    @property
    def state_class(self):
        return "measurement"
    
    @property
    def device_class(self):
        return "monetary"

    @property
    def unit_of_measurement(self):
        return "억 원"


class NaverLandMaxPriceSensor(NaverLandSensorBase):
    """Sensor to get the maximum price from NaverLand."""

    def __init__(self, data, options):
        super().__init__(data, options, sensor_type="max-price")

    async def async_update(self):
        """Fetch the maximum price and update the state."""
        if not self.api:
            return

        articles = await self.api.get_all_articles()
        if articles:
            max_price_article = max(articles, key=lambda x: convert_price_to_float(x.dealOrWarrantPrc))
            self._value = convert_price_to_float(max_price_article.dealOrWarrantPrc)
            self._data = max_price_article.__dict__


class NaverLandMinPriceSensor(NaverLandSensorBase):
    """Sensor to get the minimum price from NaverLand."""

    def __init__(self, data, options):
        super().__init__(data, options, sensor_type="min-price")

    async def async_update(self):
        """Fetch the minimum price and update the state."""
        if not self.api:
            return

        articles = await self.api.get_all_articles()
        if articles:
            min_price_article = min(articles, key=lambda x: convert_price_to_float(x.dealOrWarrantPrc))
            self._value = convert_price_to_float(min_price_article.dealOrWarrantPrc)
            self._data = min_price_article.__dict__


class NaverLandPriceDistributionSensor(NaverLandSensorBase):
    """Sensor to get the price distribution from NaverLand."""

    def __init__(self, data, options):
        super().__init__(data, options, sensor_type="price-distribution")
        self._distribution = {}

    async def async_update(self):
        """Fetch price distribution and update the state."""
        if not self.api:
            return

        articles = await self.api.get_all_articles()
        if articles:
            distribution = {}
            for article in articles:
                # Convert price string to float
                price = convert_price_to_float(article.dealOrWarrantPrc)
                if price > 0:  # Ignore invalid or zero values
                    distribution.setdefault(price, 0)
                    distribution[price] += 1

            self._distribution = distribution
            self._value = len(distribution)

    @property
    def extra_state_attributes(self):
        """Return the price distribution as additional attributes."""
        return {"distribution": self._distribution}



async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the NaverLand sensors from a config entry."""
    data = config_entry.data
    options = config_entry.options

    async_add_entities([
        NaverLandMaxPriceSensor(data, options),
        NaverLandMinPriceSensor(data, options),
        NaverLandPriceDistributionSensor(data, options),
    ])
