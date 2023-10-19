import requests
import json
import uuid
import base64
import logging
_logger = logging.getLogger(__name__)

class WalmartAPI:
    """
    Clase para interactuar con una API utilizando solicitudes HTTP.
    
    Esta clase admite solicitudes GET, POST, PUT y DELETE, así como la gestión de tokens de autenticación y la capacidad
    de enviar cuerpos JSON o archivos binarios en las solicitudes POST.
    """
    def __init__(self, client_id, client_secret):
        """
        Inicializa una instancia de MiClienteAPI.

        :param client_id: Id de cliente de Walmart API.
        :param client_secret: Password
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = None
        self.token_expires_in = None
        self.base_url = "https://sandbox.walmartapis.com/v3"

        self.autorization = f'{client_id}:{client_secret}'
        self.encoded_string = base64.b64encode(self.autorization.encode("utf-8")).decode("utf-8")

        self.headers = {
                "WM_SVC.NAME": "Walmart Marketplace",
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "WM_MARKET": "mx",
                "Authorization": f"Basic {self.encoded_string}"
            }

        self.autenticar()
    
    # def autenticar(self, username, password, custom_headers=None, custom_body=None):
    def autenticar(self):    
        """
        Realiza la autenticación con nombre de usuario y contraseña y almacena el token de acceso.

        :return: True si la autenticación tiene éxito, False en caso contrario.
        """
        try:
            # Crear un diccionario de encabezados con los encabezados apropiados
            headers = {
                "WM_QOS.CORRELATION_ID": uuid.uuid4().hex,
            }

            headers.update(self.headers)

            # Crear un diccionario con los parametros para autenticar
            params = {
                "grant_type": "client_credentials"
            }

            auth_url = f"{self.base_url}/token"  # URL de autenticación
            auth_response = requests.post(auth_url, params=params, headers=headers)

            if auth_response.status_code == 200:
                auth_result = auth_response.json()
                self.token = auth_result.get("access_token")
                self.headers["WM_SEC.ACCESS_TOKEN"] = self.token
                return True
            else:
                _logger.warning("Autenticación fallida.")
                return False
        except Exception as e:
            _logger.warning(f"Error en la autenticación: {str(e)}")
            return False

    def send_request(self, method, endpoint, data=None, file=None, headers=None):
        """
        Envía una solicitud HTTP utilizando el método especificado.

        :param method: El método HTTP a utilizar (GET, POST, PUT o DELETE).
        :param endpoint: El endpoint o recurso al que se enviará la solicitud.
        :param data: Los datos que se enviarán en el cuerpo de la solicitud (en formato JSON).
        :param file: El archivo binario que se enviará como parte de la solicitud (opcional).
        :param headers: Los encabezados HTTP personalizados a incluir en la solicitud.
        :return: La respuesta de la API en formato JSON o None en caso de error.
        """
        try:
            # Crear un diccionario de encabezados con los encabezados personalizados, si se proporcionan
            request_headers = {
                "WM_QOS.CORRELATION_ID": uuid.uuid4().hex,
                **self.headers
            }

            # Construir la URL completa
            url = f"{self.base_url}/{endpoint}"

            # Determinar el método de solicitud y realizar la solicitud correspondiente
            if method == "GET":
                response = self.get(url, headers=request_headers)
            elif method == "POST":
                if file:
                    response = self.post_multipart(url, file, data, request_headers)
                else:
                    response = self.post_json(url, data, request_headers)
            elif method == "PUT":
                response = self.put(url, data, request_headers)
            elif method == "DELETE":
                response = self.delete(url, request_headers)
            else:
                _logger.warning(f"Método HTTP no válido: {method}")
                return None

            if response is not None:
                return response.json()
            else:
                _logger.warning(f"Solicitud {method} fallida: {response.status_code}")
                return None
        except Exception as e:
            _logger.warning(f"Error en la solicitud {method}: {str(e)}")
            return None


    def put(self, endpoint, data=None, headers=None):
        """
        Realiza una solicitud PUT a la API.

        :param endpoint: El endpoint o recurso al que se enviará la solicitud.
        :param data: Los datos que se enviarán en el cuerpo de la solicitud (en formato JSON).
        :param headers: Los encabezados HTTP personalizados a incluir en la solicitud.
        :return: La respuesta de la API en formato JSON o None en caso de error.
        """
        try:
            if headers is None:
                headers = {}

            # Convierte el JSON a una cadena JSON
            json_data = json.dumps(data)
            
            # Codifica la cadena JSON en bytes
            bytes_data = json_data.encode('utf-8')

            response = requests.put(endpoint, data=bytes_data, headers=headers)

            # Verificar si la solicitud fue exitosa (código de estado 200)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:  # Token vencido
                self.autenticar()  # Intentar actualizar el token y reintentar la solicitud
                response = requests.put(endpoint, data=bytes_data, headers=headers)
                if response.status_code == 200:
                    return response.json()
            else:
                _logger.warning(f"Solicitud PUT fallida. Código de estado: {response.status_code}")
                return None
        except Exception as e:
            _logger.warning(f"Error en la solicitud PUT: {str(e)}")
            return None

    def delete(self, endpoint, headers=None):
        """
        Realiza una solicitud DELETE a la API.

        :param endpoint: El endpoint o recurso que se eliminará.
        :param headers: Los encabezados HTTP personalizados a incluir en la solicitud.
        :return: True si la eliminación tiene éxito, False en caso contrario.
        """
        try:
            if headers is None:
                headers = {}

            response = requests.delete(endpoint, headers=headers)

            # Verificar si la solicitud fue exitosa (código de estado 204 para una eliminación exitosa)
            if response.status_code == 204:
                return True
            elif response.status_code == 401:  # Token vencido
                self.autenticar()  # Intentar actualizar el token y reintentar la solicitud
                response = requests.delete(endpoint, headers=headers)
                if response.status_code == 204:
                    return True
            else:
                _logger.warning(f"Solicitud DELETE fallida. Código de estado: {response.status_code}")
                return False
        except Exception as e:
            _logger.warning(f"Error en la solicitud DELETE: {str(e)}")
            return False

    def get(self, endpoint, headers=None):
        """
        Realiza una solicitud GET a la API.

        :param endpoint: El endpoint o recurso al que se enviará la solicitud GET.
        :param headers: Los encabezados HTTP personalizados a incluir en la solicitud.
        :return: La respuesta de la API en formato JSON o None en caso de error.
        """
        try:
            if headers is None:
                headers = {}

            response = requests.get(endpoint, headers=headers)

            # Verificar si la solicitud fue exitosa (código de estado 200)
            if response.status_code == 200:
                return response
            elif response.status_code == 401:  # Token vencido
                self.autenticar()  # Intentar actualizar el token y reintentar la solicitud
                response = self.get(endpoint, headers=headers)
                if response.status_code == 200:
                    return response
            else:
                _logger.warning(f"Solicitud GET fallida. Código de estado: {response.status_code}")
                return None
        except Exception as e:
            _logger.warning(f"Error en la solicitud GET: {str(e)}")
            return None

    def post(self, endpoint, data=None, file=None, headers=None):
        """
        Realiza una solicitud POST a la API.

        :param endpoint: El endpoint o recurso al que se enviará la solicitud.
        :param data: Los datos que se enviarán en el cuerpo de la solicitud (en formato JSON).
        :param file: El archivo binario que se enviará como parte de la solicitud (opcional).
        :param headers: Los encabezados HTTP personalizados a incluir en la solicitud.
        :return: La respuesta de la API en formato JSON o None en caso de error.
        """
        try:
            if headers is None:
                headers = {}

            if file:
                # Si se proporciona un archivo, crea una solicitud multipart/form-data
                response = self.post_multipart(endpoint, file, data, headers)
            else:
                # Si no se proporciona un archivo, envía un JSON como cuerpo
                response = self.post_json(endpoint, data, headers)

            # Verificar si la solicitud fue exitosa
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 201:
                return response.json()
            elif response.status_code == 401:  # Token vencido
                self.autenticar()  # Intentar actualizar el token y reintentar la solicitud

                if file:
                    response = self.post_multipart(endpoint, file, data, headers)
                else:
                    response = self.post_json(endpoint, data, headers)

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 201:
                    return response.json()
            else:
                _logger.warning(f"Solicitud POST fallida. Código de estado: {response.status_code}")
                return None
        except Exception as e:
            _logger.warning(f"Error en la solicitud POST: {str(e)}")
            return None

    def post_json(self, url, data, headers):
        """
        Realiza una solicitud POST con datos JSON a la API.

        :param url: La URL a la que se enviará la solicitud POST.
        :param data: Los datos JSON que se enviarán en el cuerpo de la solicitud.
        :param headers: Los encabezados HTTP personalizados a incluir en la solicitud.
        :return: La respuesta de la API en formato JSON o None en caso de error.
        """
        # Convierte el JSON a una cadena JSON
        json_data = json.dumps(data)
        headers["Content-Type"] = "application/json"

        response = requests.post(url, data=json_data, headers=headers)
        return response

    def post_multipart(self, url, file, data, headers):
        """
        Realiza una solicitud POST multipart/form-data a la API.

        :param url: La URL a la que se enviará la solicitud POST.
        :param file: El archivo binario que se enviará como parte de la solicitud.
        :param data: Los datos adicionales que se enviarán en la solicitud (opcional).
        :param headers: Los encabezados HTTP personalizados a incluir en la solicitud.
        :return: La respuesta de la API en formato JSON o None en caso de error.
        """
        # files = {'file': (file['filename'], file['content'])}

        response = requests.post(url, files=file, data=data, headers=headers)
        return response