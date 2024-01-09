variable "location" {
  description = "The location/region in which to create the Azure resources"
  default     = "East US"
}

variable "resource_group_name" {
  description = "The name of the resource group in which to create the Azure resources"
}

variable "storage_account_name" {
  description = "The name of the storage account"
}

variable "function_app_name" {
  description = "The name of the function app"
}
