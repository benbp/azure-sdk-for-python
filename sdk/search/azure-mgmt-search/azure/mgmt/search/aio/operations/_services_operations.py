# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------
from typing import Any, AsyncIterable, Callable, Dict, Generic, Optional, TypeVar, Union
import warnings

from azure.core.async_paging import AsyncItemPaged, AsyncList
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError, ResourceExistsError, ResourceNotFoundError, map_error
from azure.core.pipeline import PipelineResponse
from azure.core.pipeline.transport import AsyncHttpResponse, HttpRequest
from azure.core.polling import AsyncLROPoller, AsyncNoPolling, AsyncPollingMethod
from azure.mgmt.core.exceptions import ARMErrorFormat
from azure.mgmt.core.polling.async_arm_polling import AsyncARMPolling

from ... import models as _models

T = TypeVar('T')
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, AsyncHttpResponse], T, Dict[str, Any]], Any]]

class ServicesOperations:
    """ServicesOperations async operations.

    You should not instantiate this class directly. Instead, you should create a Client instance that
    instantiates it for you and attaches it as an attribute.

    :ivar models: Alias to model classes used in this operation group.
    :type models: ~azure.mgmt.search.models
    :param client: Client for service requests.
    :param config: Configuration of service client.
    :param serializer: An object model serializer.
    :param deserializer: An object model deserializer.
    """

    models = _models

    def __init__(self, client, config, serializer, deserializer) -> None:
        self._client = client
        self._serialize = serializer
        self._deserialize = deserializer
        self._config = config

    async def _create_or_update_initial(
        self,
        resource_group_name: str,
        search_service_name: str,
        service: "_models.SearchService",
        search_management_request_options: Optional["_models.SearchManagementRequestOptions"] = None,
        **kwargs
    ) -> "_models.SearchService":
        cls = kwargs.pop('cls', None)  # type: ClsType["_models.SearchService"]
        error_map = {
            401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError
        }
        error_map.update(kwargs.pop('error_map', {}))
        
        _client_request_id = None
        if search_management_request_options is not None:
            _client_request_id = search_management_request_options.client_request_id
        api_version = "2020-08-01"
        content_type = kwargs.pop("content_type", "application/json")
        accept = "application/json"

        # Construct URL
        url = self._create_or_update_initial.metadata['url']  # type: ignore
        path_format_arguments = {
            'resourceGroupName': self._serialize.url("resource_group_name", resource_group_name, 'str'),
            'searchServiceName': self._serialize.url("search_service_name", search_service_name, 'str'),
            'subscriptionId': self._serialize.url("self._config.subscription_id", self._config.subscription_id, 'str'),
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}  # type: Dict[str, Any]
        query_parameters['api-version'] = self._serialize.query("api_version", api_version, 'str')

        # Construct headers
        header_parameters = {}  # type: Dict[str, Any]
        if _client_request_id is not None:
            header_parameters['x-ms-client-request-id'] = self._serialize.header("client_request_id", _client_request_id, 'str')
        header_parameters['Content-Type'] = self._serialize.header("content_type", content_type, 'str')
        header_parameters['Accept'] = self._serialize.header("accept", accept, 'str')

        body_content_kwargs = {}  # type: Dict[str, Any]
        body_content = self._serialize.body(service, 'SearchService')
        body_content_kwargs['content'] = body_content
        request = self._client.put(url, query_parameters, header_parameters, **body_content_kwargs)
        pipeline_response = await self._client._pipeline.run(request, stream=False, **kwargs)
        response = pipeline_response.http_response

        if response.status_code not in [200, 201]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response, error_format=ARMErrorFormat)

        if response.status_code == 200:
            deserialized = self._deserialize('SearchService', pipeline_response)

        if response.status_code == 201:
            deserialized = self._deserialize('SearchService', pipeline_response)

        if cls:
            return cls(pipeline_response, deserialized, {})

        return deserialized
    _create_or_update_initial.metadata = {'url': '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Search/searchServices/{searchServiceName}'}  # type: ignore

    async def begin_create_or_update(
        self,
        resource_group_name: str,
        search_service_name: str,
        service: "_models.SearchService",
        search_management_request_options: Optional["_models.SearchManagementRequestOptions"] = None,
        **kwargs
    ) -> AsyncLROPoller["_models.SearchService"]:
        """Creates or updates a search service in the given resource group. If the search service already
        exists, all properties will be updated with the given values.

        :param resource_group_name: The name of the resource group within the current subscription. You
         can obtain this value from the Azure Resource Manager API or the portal.
        :type resource_group_name: str
        :param search_service_name: The name of the Azure Cognitive Search service to create or update.
         Search service names must only contain lowercase letters, digits or dashes, cannot use dash as
         the first two or last one characters, cannot contain consecutive dashes, and must be between 2
         and 60 characters in length. Search service names must be globally unique since they are part
         of the service URI (https://:code:`<name>`.search.windows.net). You cannot change the service
         name after the service is created.
        :type search_service_name: str
        :param service: The definition of the search service to create or update.
        :type service: ~azure.mgmt.search.models.SearchService
        :param search_management_request_options: Parameter group.
        :type search_management_request_options: ~azure.mgmt.search.models.SearchManagementRequestOptions
        :keyword callable cls: A custom type or function that will be passed the direct response
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :keyword polling: True for ARMPolling, False for no polling, or a
         polling object for personal polling strategy
        :paramtype polling: bool or ~azure.core.polling.AsyncPollingMethod
        :keyword int polling_interval: Default waiting time between two polls for LRO operations if no Retry-After header is present.
        :return: An instance of AsyncLROPoller that returns either SearchService or the result of cls(response)
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.mgmt.search.models.SearchService]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        polling = kwargs.pop('polling', True)  # type: Union[bool, AsyncPollingMethod]
        cls = kwargs.pop('cls', None)  # type: ClsType["_models.SearchService"]
        lro_delay = kwargs.pop(
            'polling_interval',
            self._config.polling_interval
        )
        cont_token = kwargs.pop('continuation_token', None)  # type: Optional[str]
        if cont_token is None:
            raw_result = await self._create_or_update_initial(
                resource_group_name=resource_group_name,
                search_service_name=search_service_name,
                service=service,
                search_management_request_options=search_management_request_options,
                cls=lambda x,y,z: x,
                **kwargs
            )

        kwargs.pop('error_map', None)
        kwargs.pop('content_type', None)

        def get_long_running_output(pipeline_response):
            deserialized = self._deserialize('SearchService', pipeline_response)

            if cls:
                return cls(pipeline_response, deserialized, {})
            return deserialized

        path_format_arguments = {
            'resourceGroupName': self._serialize.url("resource_group_name", resource_group_name, 'str'),
            'searchServiceName': self._serialize.url("search_service_name", search_service_name, 'str'),
            'subscriptionId': self._serialize.url("self._config.subscription_id", self._config.subscription_id, 'str'),
        }

        if polling is True: polling_method = AsyncARMPolling(lro_delay, path_format_arguments=path_format_arguments,  **kwargs)
        elif polling is False: polling_method = AsyncNoPolling()
        else: polling_method = polling
        if cont_token:
            return AsyncLROPoller.from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output
            )
        else:
            return AsyncLROPoller(self._client, raw_result, get_long_running_output, polling_method)
    begin_create_or_update.metadata = {'url': '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Search/searchServices/{searchServiceName}'}  # type: ignore

    async def update(
        self,
        resource_group_name: str,
        search_service_name: str,
        service: "_models.SearchServiceUpdate",
        search_management_request_options: Optional["_models.SearchManagementRequestOptions"] = None,
        **kwargs
    ) -> "_models.SearchService":
        """Updates an existing search service in the given resource group.

        :param resource_group_name: The name of the resource group within the current subscription. You
         can obtain this value from the Azure Resource Manager API or the portal.
        :type resource_group_name: str
        :param search_service_name: The name of the Azure Cognitive Search service to update.
        :type search_service_name: str
        :param service: The definition of the search service to update.
        :type service: ~azure.mgmt.search.models.SearchServiceUpdate
        :param search_management_request_options: Parameter group.
        :type search_management_request_options: ~azure.mgmt.search.models.SearchManagementRequestOptions
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: SearchService, or the result of cls(response)
        :rtype: ~azure.mgmt.search.models.SearchService
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        cls = kwargs.pop('cls', None)  # type: ClsType["_models.SearchService"]
        error_map = {
            401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError
        }
        error_map.update(kwargs.pop('error_map', {}))
        
        _client_request_id = None
        if search_management_request_options is not None:
            _client_request_id = search_management_request_options.client_request_id
        api_version = "2020-08-01"
        content_type = kwargs.pop("content_type", "application/json")
        accept = "application/json"

        # Construct URL
        url = self.update.metadata['url']  # type: ignore
        path_format_arguments = {
            'resourceGroupName': self._serialize.url("resource_group_name", resource_group_name, 'str'),
            'searchServiceName': self._serialize.url("search_service_name", search_service_name, 'str'),
            'subscriptionId': self._serialize.url("self._config.subscription_id", self._config.subscription_id, 'str'),
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}  # type: Dict[str, Any]
        query_parameters['api-version'] = self._serialize.query("api_version", api_version, 'str')

        # Construct headers
        header_parameters = {}  # type: Dict[str, Any]
        if _client_request_id is not None:
            header_parameters['x-ms-client-request-id'] = self._serialize.header("client_request_id", _client_request_id, 'str')
        header_parameters['Content-Type'] = self._serialize.header("content_type", content_type, 'str')
        header_parameters['Accept'] = self._serialize.header("accept", accept, 'str')

        body_content_kwargs = {}  # type: Dict[str, Any]
        body_content = self._serialize.body(service, 'SearchServiceUpdate')
        body_content_kwargs['content'] = body_content
        request = self._client.patch(url, query_parameters, header_parameters, **body_content_kwargs)
        pipeline_response = await self._client._pipeline.run(request, stream=False, **kwargs)
        response = pipeline_response.http_response

        if response.status_code not in [200]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response, error_format=ARMErrorFormat)

        deserialized = self._deserialize('SearchService', pipeline_response)

        if cls:
            return cls(pipeline_response, deserialized, {})

        return deserialized
    update.metadata = {'url': '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Search/searchServices/{searchServiceName}'}  # type: ignore

    async def get(
        self,
        resource_group_name: str,
        search_service_name: str,
        search_management_request_options: Optional["_models.SearchManagementRequestOptions"] = None,
        **kwargs
    ) -> "_models.SearchService":
        """Gets the search service with the given name in the given resource group.

        :param resource_group_name: The name of the resource group within the current subscription. You
         can obtain this value from the Azure Resource Manager API or the portal.
        :type resource_group_name: str
        :param search_service_name: The name of the Azure Cognitive Search service associated with the
         specified resource group.
        :type search_service_name: str
        :param search_management_request_options: Parameter group.
        :type search_management_request_options: ~azure.mgmt.search.models.SearchManagementRequestOptions
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: SearchService, or the result of cls(response)
        :rtype: ~azure.mgmt.search.models.SearchService
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        cls = kwargs.pop('cls', None)  # type: ClsType["_models.SearchService"]
        error_map = {
            401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError
        }
        error_map.update(kwargs.pop('error_map', {}))
        
        _client_request_id = None
        if search_management_request_options is not None:
            _client_request_id = search_management_request_options.client_request_id
        api_version = "2020-08-01"
        accept = "application/json"

        # Construct URL
        url = self.get.metadata['url']  # type: ignore
        path_format_arguments = {
            'resourceGroupName': self._serialize.url("resource_group_name", resource_group_name, 'str'),
            'searchServiceName': self._serialize.url("search_service_name", search_service_name, 'str'),
            'subscriptionId': self._serialize.url("self._config.subscription_id", self._config.subscription_id, 'str'),
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}  # type: Dict[str, Any]
        query_parameters['api-version'] = self._serialize.query("api_version", api_version, 'str')

        # Construct headers
        header_parameters = {}  # type: Dict[str, Any]
        if _client_request_id is not None:
            header_parameters['x-ms-client-request-id'] = self._serialize.header("client_request_id", _client_request_id, 'str')
        header_parameters['Accept'] = self._serialize.header("accept", accept, 'str')

        request = self._client.get(url, query_parameters, header_parameters)
        pipeline_response = await self._client._pipeline.run(request, stream=False, **kwargs)
        response = pipeline_response.http_response

        if response.status_code not in [200]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response, error_format=ARMErrorFormat)

        deserialized = self._deserialize('SearchService', pipeline_response)

        if cls:
            return cls(pipeline_response, deserialized, {})

        return deserialized
    get.metadata = {'url': '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Search/searchServices/{searchServiceName}'}  # type: ignore

    async def delete(
        self,
        resource_group_name: str,
        search_service_name: str,
        search_management_request_options: Optional["_models.SearchManagementRequestOptions"] = None,
        **kwargs
    ) -> None:
        """Deletes a search service in the given resource group, along with its associated resources.

        :param resource_group_name: The name of the resource group within the current subscription. You
         can obtain this value from the Azure Resource Manager API or the portal.
        :type resource_group_name: str
        :param search_service_name: The name of the Azure Cognitive Search service associated with the
         specified resource group.
        :type search_service_name: str
        :param search_management_request_options: Parameter group.
        :type search_management_request_options: ~azure.mgmt.search.models.SearchManagementRequestOptions
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: None, or the result of cls(response)
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        cls = kwargs.pop('cls', None)  # type: ClsType[None]
        error_map = {
            401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError
        }
        error_map.update(kwargs.pop('error_map', {}))
        
        _client_request_id = None
        if search_management_request_options is not None:
            _client_request_id = search_management_request_options.client_request_id
        api_version = "2020-08-01"
        accept = "application/json"

        # Construct URL
        url = self.delete.metadata['url']  # type: ignore
        path_format_arguments = {
            'resourceGroupName': self._serialize.url("resource_group_name", resource_group_name, 'str'),
            'searchServiceName': self._serialize.url("search_service_name", search_service_name, 'str'),
            'subscriptionId': self._serialize.url("self._config.subscription_id", self._config.subscription_id, 'str'),
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}  # type: Dict[str, Any]
        query_parameters['api-version'] = self._serialize.query("api_version", api_version, 'str')

        # Construct headers
        header_parameters = {}  # type: Dict[str, Any]
        if _client_request_id is not None:
            header_parameters['x-ms-client-request-id'] = self._serialize.header("client_request_id", _client_request_id, 'str')
        header_parameters['Accept'] = self._serialize.header("accept", accept, 'str')

        request = self._client.delete(url, query_parameters, header_parameters)
        pipeline_response = await self._client._pipeline.run(request, stream=False, **kwargs)
        response = pipeline_response.http_response

        if response.status_code not in [200, 204, 404]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response, error_format=ARMErrorFormat)

        if cls:
            return cls(pipeline_response, None, {})

    delete.metadata = {'url': '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Search/searchServices/{searchServiceName}'}  # type: ignore

    def list_by_resource_group(
        self,
        resource_group_name: str,
        search_management_request_options: Optional["_models.SearchManagementRequestOptions"] = None,
        **kwargs
    ) -> AsyncIterable["_models.SearchServiceListResult"]:
        """Gets a list of all search services in the given resource group.

        :param resource_group_name: The name of the resource group within the current subscription. You
         can obtain this value from the Azure Resource Manager API or the portal.
        :type resource_group_name: str
        :param search_management_request_options: Parameter group.
        :type search_management_request_options: ~azure.mgmt.search.models.SearchManagementRequestOptions
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: An iterator like instance of either SearchServiceListResult or the result of cls(response)
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.mgmt.search.models.SearchServiceListResult]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        cls = kwargs.pop('cls', None)  # type: ClsType["_models.SearchServiceListResult"]
        error_map = {
            401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError
        }
        error_map.update(kwargs.pop('error_map', {}))
        
        _client_request_id = None
        if search_management_request_options is not None:
            _client_request_id = search_management_request_options.client_request_id
        api_version = "2020-08-01"
        accept = "application/json"

        def prepare_request(next_link=None):
            # Construct headers
            header_parameters = {}  # type: Dict[str, Any]
            if _client_request_id is not None:
                header_parameters['x-ms-client-request-id'] = self._serialize.header("client_request_id", _client_request_id, 'str')
            header_parameters['Accept'] = self._serialize.header("accept", accept, 'str')

            if not next_link:
                # Construct URL
                url = self.list_by_resource_group.metadata['url']  # type: ignore
                path_format_arguments = {
                    'resourceGroupName': self._serialize.url("resource_group_name", resource_group_name, 'str'),
                    'subscriptionId': self._serialize.url("self._config.subscription_id", self._config.subscription_id, 'str'),
                }
                url = self._client.format_url(url, **path_format_arguments)
                # Construct parameters
                query_parameters = {}  # type: Dict[str, Any]
                query_parameters['api-version'] = self._serialize.query("api_version", api_version, 'str')

                request = self._client.get(url, query_parameters, header_parameters)
            else:
                url = next_link
                query_parameters = {}  # type: Dict[str, Any]
                request = self._client.get(url, query_parameters, header_parameters)
            return request

        async def extract_data(pipeline_response):
            deserialized = self._deserialize('SearchServiceListResult', pipeline_response)
            list_of_elem = deserialized.value
            if cls:
                list_of_elem = cls(list_of_elem)
            return deserialized.next_link or None, AsyncList(list_of_elem)

        async def get_next(next_link=None):
            request = prepare_request(next_link)

            pipeline_response = await self._client._pipeline.run(request, stream=False, **kwargs)
            response = pipeline_response.http_response

            if response.status_code not in [200]:
                map_error(status_code=response.status_code, response=response, error_map=error_map)
                raise HttpResponseError(response=response, error_format=ARMErrorFormat)

            return pipeline_response

        return AsyncItemPaged(
            get_next, extract_data
        )
    list_by_resource_group.metadata = {'url': '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Search/searchServices'}  # type: ignore

    def list_by_subscription(
        self,
        search_management_request_options: Optional["_models.SearchManagementRequestOptions"] = None,
        **kwargs
    ) -> AsyncIterable["_models.SearchServiceListResult"]:
        """Gets a list of all search services in the given subscription.

        :param search_management_request_options: Parameter group.
        :type search_management_request_options: ~azure.mgmt.search.models.SearchManagementRequestOptions
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: An iterator like instance of either SearchServiceListResult or the result of cls(response)
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.mgmt.search.models.SearchServiceListResult]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        cls = kwargs.pop('cls', None)  # type: ClsType["_models.SearchServiceListResult"]
        error_map = {
            401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError
        }
        error_map.update(kwargs.pop('error_map', {}))
        
        _client_request_id = None
        if search_management_request_options is not None:
            _client_request_id = search_management_request_options.client_request_id
        api_version = "2020-08-01"
        accept = "application/json"

        def prepare_request(next_link=None):
            # Construct headers
            header_parameters = {}  # type: Dict[str, Any]
            if _client_request_id is not None:
                header_parameters['x-ms-client-request-id'] = self._serialize.header("client_request_id", _client_request_id, 'str')
            header_parameters['Accept'] = self._serialize.header("accept", accept, 'str')

            if not next_link:
                # Construct URL
                url = self.list_by_subscription.metadata['url']  # type: ignore
                path_format_arguments = {
                    'subscriptionId': self._serialize.url("self._config.subscription_id", self._config.subscription_id, 'str'),
                }
                url = self._client.format_url(url, **path_format_arguments)
                # Construct parameters
                query_parameters = {}  # type: Dict[str, Any]
                query_parameters['api-version'] = self._serialize.query("api_version", api_version, 'str')

                request = self._client.get(url, query_parameters, header_parameters)
            else:
                url = next_link
                query_parameters = {}  # type: Dict[str, Any]
                request = self._client.get(url, query_parameters, header_parameters)
            return request

        async def extract_data(pipeline_response):
            deserialized = self._deserialize('SearchServiceListResult', pipeline_response)
            list_of_elem = deserialized.value
            if cls:
                list_of_elem = cls(list_of_elem)
            return deserialized.next_link or None, AsyncList(list_of_elem)

        async def get_next(next_link=None):
            request = prepare_request(next_link)

            pipeline_response = await self._client._pipeline.run(request, stream=False, **kwargs)
            response = pipeline_response.http_response

            if response.status_code not in [200]:
                map_error(status_code=response.status_code, response=response, error_map=error_map)
                raise HttpResponseError(response=response, error_format=ARMErrorFormat)

            return pipeline_response

        return AsyncItemPaged(
            get_next, extract_data
        )
    list_by_subscription.metadata = {'url': '/subscriptions/{subscriptionId}/providers/Microsoft.Search/searchServices'}  # type: ignore

    async def check_name_availability(
        self,
        name: str,
        search_management_request_options: Optional["_models.SearchManagementRequestOptions"] = None,
        **kwargs
    ) -> "_models.CheckNameAvailabilityOutput":
        """Checks whether or not the given search service name is available for use. Search service names
        must be globally unique since they are part of the service URI
        (https://:code:`<name>`.search.windows.net).

        :param name: The search service name to validate. Search service names must only contain
         lowercase letters, digits or dashes, cannot use dash as the first two or last one characters,
         cannot contain consecutive dashes, and must be between 2 and 60 characters in length.
        :type name: str
        :param search_management_request_options: Parameter group.
        :type search_management_request_options: ~azure.mgmt.search.models.SearchManagementRequestOptions
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: CheckNameAvailabilityOutput, or the result of cls(response)
        :rtype: ~azure.mgmt.search.models.CheckNameAvailabilityOutput
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        cls = kwargs.pop('cls', None)  # type: ClsType["_models.CheckNameAvailabilityOutput"]
        error_map = {
            401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError
        }
        error_map.update(kwargs.pop('error_map', {}))
        
        _client_request_id = None
        if search_management_request_options is not None:
            _client_request_id = search_management_request_options.client_request_id

        _check_name_availability_input = _models.CheckNameAvailabilityInput(name=name)
        api_version = "2020-08-01"
        content_type = kwargs.pop("content_type", "application/json")
        accept = "application/json"

        # Construct URL
        url = self.check_name_availability.metadata['url']  # type: ignore
        path_format_arguments = {
            'subscriptionId': self._serialize.url("self._config.subscription_id", self._config.subscription_id, 'str'),
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}  # type: Dict[str, Any]
        query_parameters['api-version'] = self._serialize.query("api_version", api_version, 'str')

        # Construct headers
        header_parameters = {}  # type: Dict[str, Any]
        if _client_request_id is not None:
            header_parameters['x-ms-client-request-id'] = self._serialize.header("client_request_id", _client_request_id, 'str')
        header_parameters['Content-Type'] = self._serialize.header("content_type", content_type, 'str')
        header_parameters['Accept'] = self._serialize.header("accept", accept, 'str')

        body_content_kwargs = {}  # type: Dict[str, Any]
        body_content = self._serialize.body(_check_name_availability_input, 'CheckNameAvailabilityInput')
        body_content_kwargs['content'] = body_content
        request = self._client.post(url, query_parameters, header_parameters, **body_content_kwargs)
        pipeline_response = await self._client._pipeline.run(request, stream=False, **kwargs)
        response = pipeline_response.http_response

        if response.status_code not in [200]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response, error_format=ARMErrorFormat)

        deserialized = self._deserialize('CheckNameAvailabilityOutput', pipeline_response)

        if cls:
            return cls(pipeline_response, deserialized, {})

        return deserialized
    check_name_availability.metadata = {'url': '/subscriptions/{subscriptionId}/providers/Microsoft.Search/checkNameAvailability'}  # type: ignore
