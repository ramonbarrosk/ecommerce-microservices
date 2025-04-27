provider "aws" {
  region = "us-east-1"
}

data "aws_region" "current" {}

resource "aws_lambda_function" "orders" {
  filename         = "../services/orders/deploy.zip"
  function_name    = "orders-service"
  handler          = "handler.lambda_handler"
  runtime          = "python3.11"
  role             = aws_iam_role.lambda_exec.arn
  source_code_hash = filebase64sha256("../services/orders/deploy.zip")
}


resource "aws_api_gateway_rest_api" "orders_api" {
  name        = "orders-api"
  description = "API Gateway for orders-service"
}

resource "aws_api_gateway_resource" "orders_resource" {
  rest_api_id = aws_api_gateway_rest_api.orders_api.id
  parent_id   = aws_api_gateway_rest_api.orders_api.root_resource_id
  path_part   = "orders"
}

resource "aws_api_gateway_method" "orders_get_method" {
  rest_api_id   = aws_api_gateway_rest_api.orders_api.id
  resource_id   = aws_api_gateway_resource.orders_resource.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "orders_lambda_integration" {
  rest_api_id = aws_api_gateway_rest_api.orders_api.id
  resource_id = aws_api_gateway_resource.orders_resource.id
  http_method = aws_api_gateway_method.orders_get_method.http_method
  integration_http_method = "POST"
  type = "AWS_PROXY"
  uri = "arn:aws:apigateway:${data.aws_region.current.name}:lambda:path/2015-03-31/functions/${aws_lambda_function.orders.arn}/invocations"
}


resource "aws_lambda_permission" "allow_api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.orders.function_name
  principal     = "apigateway.amazonaws.com"
}

resource "aws_api_gateway_deployment" "orders_api_deployment" {
  depends_on = [
    aws_api_gateway_integration.orders_lambda_integration
  ]
  rest_api_id = aws_api_gateway_rest_api.orders_api.id
  stage_name  = "prod"
}

output "api_url" {
  value = "https://${aws_api_gateway_rest_api.orders_api.id}.execute-api.${data.aws_region.current.name}.amazonaws.com/prod/orders"
}

resource "aws_iam_role" "lambda_exec" {
  name = "lambda_execution_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}