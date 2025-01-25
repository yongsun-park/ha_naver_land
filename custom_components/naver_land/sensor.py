import asyncio
from collections import defaultdict
from datetime import datetime
import datetime
import logging
import hashlib
from .naver_land import NaverLandApi
from homeassistant.helpers.entity import Entity
from .const import DOMAIN
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = datetime.timedelta(minutes=60)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the sensor platform."""
    config_data = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([NaverLandMaxPrice(config_data)], False)
    async_add_entities([NaverLandMinPrice(config_data)], False)
    async_add_entities([NaverLandPriceDistribution(config_data)], False)


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


class NaverLandMaxPrice(Entity):
    def __init__(self, config_data):
        self.api = NaverLandApi(
            apt_id=config_data["apt_id"],
            area=config_data["area"],
            exclude_low_floors=config_data.get("exclude_low_floors", False),
            low_floor_limit=config_data.get("low_floor_limit", 5)
        )
        self._name = f"{self.api.apt_id}-max-price"
        self.device_id = hashlib.md5(f"{self.api.apt_id}-max".encode("UTF-8")).hexdigest()
        self._data = None
        self._value = None
        asyncio.create_task(self.async_update())

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        await self.async_update()

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self.device_id

    @property
    def state(self):
        return self._value

    @property
    def available(self):
        """Could the device be accessed during the last update call."""
        return self._data is not None

    @property
    def extra_state_attributes(self):
        return self._data

    @property
    def state_class(self):
        return "measurement"

    @property
    def device_class(self):
        return "pm25"

    async def async_update(self):
        articles = await self.api.get_all_articles()
        if articles:
            max_price_article = max(articles, key=lambda x: convert_price_to_float(x.dealOrWarrantPrc))
            self._data = max_price_article.__dict__
            self._value = convert_price_to_float(max_price_article.dealOrWarrantPrc)


class NaverLandMinPrice(Entity):
    def __init__(self, config_data):
        # NaverLandApi 초기화
        self.api = NaverLandApi(
            apt_id=config_data["apt_id"],
            area=config_data["area"],
            exclude_low_floors=config_data.get("exclude_low_floors", False),
            low_floor_limit=config_data.get("low_floor_limit", 5)
        )
        # 센서 기본 정보 설정
        self._name = f"{self.api.apt_id}-min-price"
        self.device_id = hashlib.md5(f"{self.api.apt_id}-min".encode("UTF-8")).hexdigest()
        self._data = None
        self._value = None
        asyncio.create_task(self.async_update())

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        await self.async_update()

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self.device_id

    @property
    def state(self):
        return self._value

    @property
    def available(self):
        """Could the device be accessed during the last update call."""
        return self._data is not None

    @property
    def extra_state_attributes(self):
        return self._data

    @property
    def state_class(self):
        return "measurement"

    @property
    def device_class(self):
        return "pm25"

    async def async_update(self):
        articles = await self.api.get_all_articles()
        if articles:
            min_price_article = min(articles, key=lambda x: convert_price_to_float(x.dealOrWarrantPrc))
            self._data = min_price_article.__dict__
            self._value = convert_price_to_float(min_price_article.dealOrWarrantPrc)


class NaverLandPriceDistribution(Entity):
    def __init__(self, config_data):
        # NaverLandApi 초기화
        self.api = NaverLandApi(
            apt_id=config_data["apt_id"],
            area=config_data["area"],
            exclude_low_floors=config_data.get("exclude_low_floors", False),
            low_floor_limit=config_data.get("low_floor_limit", 5)
        )
        # 센서 기본 정보 설정
        self._name = f"{self.api.apt_id}-price-distribution"
        self.device_id = hashlib.md5(f"{self.api.apt_id}-price-dist".encode("UTF-8")).hexdigest()
        self._data = defaultdict(list)
        self._value = None
        asyncio.create_task(self.async_update())

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        await self.async_update()

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self.device_id

    @property
    def state(self):
        return self._value

    @property
    def available(self):
        """Could the device be accessed during the last update call."""
        return self._data is not None

    @property
    def state_class(self):
        return "measurement"

    @property
    def extra_state_attributes(self):
        return self._data

    @property
    def device_class(self):
        return "pm25"

    async def async_update(self):
        articles = await self.api.get_all_articles()
        if articles:
            for article in articles:
                date = datetime.datetime.strptime(article.articleConfirmYmd, '%Y%m%d')
                price = convert_price_to_float(article.dealOrWarrantPrc)
                self._data[date].append(price)
            self._value = sum(len(prices) for prices in self._data.values())

    @property
    def extra_state_attributes(self):
        return {str(date): prices for date, prices in self._data.items()}
