#from azure.common.credentials import UserPassCredentials
import os
from haikunator import Haikunator
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.storage.models import (
    StorageAccountCreateParameters,
    StorageAccountUpdateParameters,
    Sku,
    SkuName,
    Kind
)
from azure.storage import CloudStorageAccount
from azure.storage.blob.models import ContentSettings

WEST_US = 'westus'
GROUP_NAME = 'my_resource_group'
#STORAGE_ACCOUNT_NAME = Haikunator().haikunate(delimiter='')
STORAGE_ACCOUNT_NAME = 'coldsun5938'

def print_item(group):
    """Print an Azure object instance."""
    print("\tName: {}".format(group.name))
    print("\tId: {}".format(group.id))
    print("\tLocation: {}".format(group.location))
    print("\tTags: {}".format(group.tags))
    if hasattr(group, 'properties'):
        print_properties(group.properties)

def print_properties(props):
    """Print a ResourceGroup properties instance."""
    if props and props.provisioning_state:
        print("\tProperties:")
        print("\t\tProvisioning State: {}".format(props.provisioning_state))
    print("\n\n")

#credentials = UserPassCredentials('muztagh_7546@muztagh7546hotmail.onmicrosoft.com', 'October10')
credentials = ServicePrincipalCredentials(
    client_id = '',
    secret = '',
    tenant = ''
)
subscription_id = ''
resource_client = ResourceManagementClient(credentials, subscription_id)
storage_client = StorageManagementClient(credentials, subscription_id)

# You MIGHT need to add Storage as a valid provider for these credentials
# If so, this operation has to be done only once for each credentials
resource_client.providers.register('Microsoft.Storage')

# Create Resource group
print('Create Resource Group')
resource_group_params = {'location':'westus'}
print_item(resource_client.resource_groups.create_or_update(GROUP_NAME, resource_group_params))

# Check availability
print('Check name availability')
bad_account_name = 'invalid-or-used-name'
availability = storage_client.storage_accounts.check_name_availability(bad_account_name)
print('The account {} is available: {}'.format(bad_account_name, availability.name_available))
print('Reason: {}'.format(availability.reason))
print('Detailed message: {}'.format(availability.message))
print('\n\n')

# Create a storage account
print('Create a storage account')
storage_async_operation = storage_client.storage_accounts.create(
    GROUP_NAME,
    STORAGE_ACCOUNT_NAME,
    StorageAccountCreateParameters(
        sku=Sku(SkuName.standard_ragrs),
        kind=Kind.storage,
        location='westus'
    )
)
storage_account = storage_async_operation.result()
print_item(storage_account)
print('\n\n')

# Get the account keys
print('Get the account keys')
storage_keys = storage_client.storage_accounts.list_keys(GROUP_NAME, STORAGE_ACCOUNT_NAME)
storage_keys = {v.key_name: v.value for v in storage_keys.keys}
print('\tKey 1: {}'.format(storage_keys['key1']))
print('\tKey 2: {}'.format(storage_keys['key2']))
print("\n\n")

print('Create blob service')
storage_client = CloudStorageAccount(STORAGE_ACCOUNT_NAME, storage_keys['key1'])
blob_service = storage_client.create_block_blob_service()

print('Create container')
blob_service.create_container('muztagh-container-name')

print('Create blob')
blob_service.create_blob_from_bytes(
'muztagh-container-name',
'my-blob-name',
b'<center><h1>Hello World!</h1></center>',
content_settings=ContentSettings('text/html')
)
print(blob_service.make_blob_url('my-container-name', 'my-blob-name'))

