import pulumi
import pulumi_aws as aws

'''step-1 first create an ECR repository and put that into github secrets '''

ecr_repo = aws.ecr.Repository(
    "supplychain-ecr",
    force_delete=True
)


pulumi.export("ecr_repo_url", ecr_repo.repository_url)


'''steps are continued from here ..!'''

cluster = aws.ecs.Cluster("supplychain-cluster")

task_exec_role = aws.iam.Role(
    "ecsTaskExecutionRole",
    assume_role_policy="""{
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": { "Service": "ecs-tasks.amazonaws.com" },
            "Action": "sts:AssumeRole"
        }]
    }"""
)

aws.iam.RolePolicyAttachment(
    "ecsTaskExecutionRolePolicy",
    role=task_exec_role.name,
    policy_arn="arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
)

task_definition = aws.ecs.TaskDefinition(
    "supplychain-task",
    family="supplychain",
    cpu="256",
    memory="512",
    network_mode="awsvpc",
    requires_compatibilities=["FARGATE"],
    execution_role_arn=task_exec_role.arn,
    container_definitions=pulumi.Output.all(
        ecr_repo.repository_url
    ).apply(lambda args: f"""
    [{{
        "name": "fastapi",
        "image": "{args[0]}:latest",
        "portMappings": [{{
            "containerPort": 8000
        }}]
    }}]
    """)
)

alb = aws.lb.LoadBalancer(
    "supplychain-alb",
    internal=False,
    load_balancer_type="application",
    security_groups=[],
    subnets=aws.ec2.get_subnets().ids
)

listener = aws.lb.Listener(
    "http-listener",
    load_balancer_arn=alb.arn,
    port=80,
    default_actions=[{
        "type": "fixed-response",
        "fixedResponse": {
            "contentType": "text/plain",
            "messageBody": "Service running",
            "statusCode": "200"
        }
    }]
)

pulumi.export("api_url", alb.dns_name)
