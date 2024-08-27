from odoo.api import Environment
from ..log.logger import logger
from ..log.logger import logs
import requests
import json

def send_price_webhook(env, product, company_id, update_price):
    """
    TODO: register webhook failures in order to implement "retries"
    :param env:
    :type env: Environment
    :param product_id:
    :type product_id: int
    :param hook_id:
    :type hook_id: int
    :return:
    """
    logger.debug('### SEND PRICE WEBHOOK ###')
    product_id = product.id
    logger.debug("Producto: {}".format(product_id))
    logger.debug("Company: {}".format(company_id))
    config = env['madkting.config'].get_config()
        
    mapping_ids = env['yuju.mapping'].sudo().get_mapping(company_id)
    if mapping_ids:
        # Tiene multi shop activo
        product_mapping_ids = env['yuju.mapping.product'].get_product_mapping_by_product(product_id=product_id, only_active=True)

        if not product_mapping_ids:
            logger.exception('No se encontro mapeo de producto para ID {}'.format(product_id))
            return

        for product_mapping in product_mapping_ids:

            webhook_body = {
                'product_id': product.id,
                'default_code': product.default_code,
                'id_product_madkting': product_mapping.id_product_yuju,
                'event': 'price_update',
                'price': update_price
            }
            data = json.dumps(webhook_body)
            headers = {'Content-Type': 'application/json'}

            webhook_suscriptions = env['madkting.webhook'].search([
                ('hook_type', '=', 'price'),
                ('active', '=', True),
                ('company_id', '=', company_id),
                ('url', 'ilike', product_mapping.id_shop_yuju),
            ], limit=1)

            for webhook in webhook_suscriptions:
                """
                TODO: if the webhook fails store it into a database for retry implementation
                """
                success = send_webhook(env, webhook.url, data, headers)

    else:

        if product.id_product_madkting:
            webhook_suscriptions = env['madkting.webhook'].search([
                ('hook_type', '=', 'price'),
                ('active', '=', True),
                ('company_id', '=', company_id)
            ])
            webhook_body = {
                'product_id': product.id,
                'default_code': product.default_code,
                'id_product_madkting': product.id_product_madkting,
                'event': 'price_update',
                'price': update_price,
                # 'quantities' : ubicaciones_stock
            }
            data = json.dumps(webhook_body)
            headers = {'Content-Type': 'application/json'}
            for webhook in webhook_suscriptions:
                """
                TODO: if the webhook fails store it into a database for retry implementation
                """
                success = send_webhook(env, webhook.url, data, headers)

def send_webhook(env, url, data, headers):
    """
    :param url:
    :param data:
    :param headers:
    :return:
    """
    config = env['madkting.config'].get_config()
    logs("#### SEND PRICE WEBHOOK ####", config)
    logs(data, config)
    logs(url, config)
    logs(headers, config)
    try:
        response = requests.post(url, data=data, headers=headers)
    except Exception as ex:
        logger.exception(ex)
        return False
    else:
        if not response.ok:
            logger.error(response.text)
            return False
        return True
