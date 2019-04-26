"""Platform for Grocy integration."""
import logging

import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_URL, CONF_API_KEY
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv


_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_URL): cv.string,
    vol.Required(CONF_API_KEY): cv.string
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    from pygrocy import Grocy

    api_url = config[CONF_URL]
    password = config[CONF_API_KEY]

    _LOGGER.info("Trying to set up grocy client...")
    grocy = Grocy(api_url, password)

    _LOGGER.info("Trying to get current stock...")
    stocks = grocy.stock()

    _LOGGER.info("Got stock with %d items", len(stocks))

    add_entities(StockSensor(stock, grocy) for stock in stocks)

from homeassistant.helpers.entity import entity

class StockSensor(Entity):
    """Representation of a Sensor for a product."""

    def __init__(self, stock):
        _LOGGER.info("Setting up product with id: %s", stock['product_id'])
        self._stock = stock
    
    @property
    def state(self):
        return self._stock.amount

    @property
    def product_id(self):
        return self._stock.product_id

    @property
    def best_before_date(self):
        return self._stock.best_before_date

    def update(self):
        self._stock.update()
