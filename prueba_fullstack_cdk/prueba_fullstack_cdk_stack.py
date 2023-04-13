from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_events as events,
    aws_events_targets as targets,
)
from constructs import Construct

class PruebaFullstackCdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        #? Definimos la tabla de dynamodb
        criptos = dynamodb.Table(self, 'Criptos',
            partition_key=dynamodb.Attribute(
                name="time",
                type=dynamodb.AttributeType.STRING
            )
        )

        #! Definimos las funciones lambda para guardar los registros de las criptos y para obtener las criptos
        save_criptos = _lambda.Function(self, "SaveCriptos",
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.from_asset("lambda"),                          
            handler="lambda_criptos.save_criptos",
            environment={
                "TABLE_CRIPTOS": criptos.table_name
            }
        )

        get_criptos = _lambda.Function(self, "GetCriptos",
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.from_asset("lambda"),                          
            handler="lambda_criptos.get_criptos",
            environment={
                "TABLE_CRIPTOS": criptos.table_name
            }
        )

        #? Creamos un evento de CloudWatch Events que se dispare cada 6 horas
        rule = events.Rule(
            self, 'MyScheduledRule',
            schedule=events.Schedule.cron(minute='0', hour='*/6'),
        )

        #! Agregamos la función Lambda como destino del evento
        rule.add_target(targets.LambdaFunction(save_criptos))


        #? Le damos permisos a la función lambda para usar la tabla de dynamodb
        criptos.grant_read_write_data(save_criptos)
        criptos.grant_read_write_data(get_criptos)


        #! Creamos un apigateway para leer los valores de la tabla de dynamodb
        apiCriptos = apigw.RestApi(self, 'APICriptos', rest_api_name='API Criptos')

        get_criptos_resource = apiCriptos.root.add_resource('getCriptos')
        get_criptos_method = get_criptos_resource.add_method('GET', apigw.LambdaIntegration(handler=get_criptos))



