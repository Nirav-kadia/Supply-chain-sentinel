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
    assume_role_policy=pulumi.Output.json_dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": { "Service": "ecs-tasks.amazonaws.com" },
            "Action": "sts:AssumeRole"
        }]
    })
)

aws.iam.RolePolicyAttachment(
    "ecsTaskExecutionRolePolicy",
    role=task_exec_role.name,
    policy_arn="arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy",
    opts=pulumi.ResourceOptions(depends_on=[task_exec_role])
)

# Create CloudWatch log group for ECS logs
log_group = aws.cloudwatch.LogGroup(
    "supplychain-logs",
    name="/ecs/supplychain",
    retention_in_days=7
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
        }}],
        "environment": [
            {{
                "name": "NEO4J_URI",
                "value": "neo4j+ssc://e549a456.databases.neo4j.io"
            }},
            {{
                "name": "NEO4J_USER",
                "value": "neo4j"
            }},
            {{
                "name": "NEO4J_PASSWORD",
                "value": "n66M978Cm1zU-vdSdXCC7AGtwOw2gS1wn2UZAvHYNcI"
            }},
            {{
                "name": "GOOGLE_API_KEY",
                "value": "AIzaSyBovrkeTtXOyMYlTOQoCn6RmjDH9DTiZQ8"
            }}
        ],
        "logConfiguration": {{
            "logDriver": "awslogs",
            "options": {{
                "awslogs-group": "/ecs/supplychain",
                "awslogs-region": "us-east-1",
                "awslogs-stream-prefix": "ecs"
            }}
        }}
    }}]
    """)
)

# Get default VPC
default_vpc = aws.ec2.get_vpc(default=True)

# Create security group for ALB
alb_security_group = aws.ec2.SecurityGroup(
    "alb-security-group",
    description="Security group for Application Load Balancer",
    vpc_id=default_vpc.id,
    ingress=[
        {
            "protocol": "tcp",
            "from_port": 80,
            "to_port": 80,
            "cidr_blocks": ["0.0.0.0/0"],
            "description": "HTTP access from anywhere"
        },
        {
            "protocol": "tcp",
            "from_port": 443,
            "to_port": 443,
            "cidr_blocks": ["0.0.0.0/0"],
            "description": "HTTPS access from anywhere"
        }
    ],
    egress=[
        {
            "protocol": "-1",
            "from_port": 0,
            "to_port": 0,
            "cidr_blocks": ["0.0.0.0/0"],
            "description": "All outbound traffic"
        }
    ]
)

public_subnets = aws.ec2.get_subnets(
    filters=[{
        "name": "map-public-ip-on-launch",
        "values": ["true"]
    }]
)

alb = aws.lb.LoadBalancer(
    "supplychain-alb",
    internal=False,
    load_balancer_type="application",
    security_groups=[alb_security_group.id],
    subnets=public_subnets.ids,
)

# Create security group for ECS tasks
ecs_security_group = aws.ec2.SecurityGroup(
    "ecs-security-group",
    description="Security group for ECS tasks",
    vpc_id=default_vpc.id,
    ingress=[
        {
            "protocol": "tcp",
            "from_port": 8000,
            "to_port": 8000,
            "security_groups": [alb_security_group.id],
            "description": "Allow traffic from ALB"
        }
    ],
    egress=[
        {
            "protocol": "-1",
            "from_port": 0,
            "to_port": 0,
            "cidr_blocks": ["0.0.0.0/0"],
            "description": "All outbound traffic"
        }
    ]
)

# Create target group for ALB
target_group = aws.lb.TargetGroup(
    "supplychain-tg",
    port=8000,
    protocol="HTTP",
    vpc_id=default_vpc.id,
    target_type="ip",
    health_check={
        "enabled": True,
        "healthy_threshold": 2,
        "interval": 30,
        "matcher": "200",
        "path": "/",
        "port": "traffic-port",
        "protocol": "HTTP",
        "timeout": 10,
        "unhealthy_threshold": 3
    }
)

listener = aws.lb.Listener(
    "http-listener",
    load_balancer_arn=alb.arn,
    port=80,
    default_actions=[{
        "type": "forward",
        "target_group_arn": target_group.arn
    }]
)

# Create ECS service
service = aws.ecs.Service(
    "supplychain-service",
    cluster=cluster.id,
    task_definition=task_definition.arn,
    desired_count=1,
    launch_type="FARGATE",
    health_check_grace_period_seconds=300,
    network_configuration={
        "assign_public_ip": True,
        "subnets": public_subnets.ids,
        "security_groups": [ecs_security_group.id]
    },
    load_balancers=[{
        "target_group_arn": target_group.arn,
        "container_name": "fastapi",
        "container_port": 8000
    }],
    opts=pulumi.ResourceOptions(depends_on=[listener])
)

pulumi.export("api_url", alb.dns_name)
pulumi.export("target_group_arn", target_group.arn)
pulumi.export("cluster_name", cluster.name)
pulumi.export("service_name", service.name)
