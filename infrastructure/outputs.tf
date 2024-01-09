output "function_app_default_hostname" {
  value = azurerm_function_app.fa.default_hostname
}

output "storage_account_primary_connection_string" {
  value = azurerm_storage_account.sa.primary_connection_string
}
