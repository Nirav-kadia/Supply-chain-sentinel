#!/usr/bin/env python3
"""
Debug script to check ECS service and ALB target health
"""
import boto3
import json

def check_ecs_service():
    ecs = boto3.client('ecs', region_name='us-east-1')
    elbv2 = boto3.client('elbv2', region_name='us-east-1')
    logs = boto3.client('logs', region_name='us-east-1')
    
    print("=== ECS Service Status ===")
    try:
        services = ecs.describe_services(
            cluster='supplychain-cluster',
            services=['supplychain-service']
        )
        
        if services['services']:
            service = services['services'][0]
            print(f"Service Status: {service['status']}")
            print(f"Running Count: {service['runningCount']}")
            print(f"Pending Count: {service['pendingCount']}")
            print(f"Desired Count: {service['desiredCount']}")
            
            # Get tasks
            tasks = ecs.list_tasks(
                cluster='supplychain-cluster',
                serviceName='supplychain-service'
            )
            
            if tasks['taskArns']:
                task_details = ecs.describe_tasks(
                    cluster='supplychain-cluster',
                    tasks=tasks['taskArns']
                )
                
                for task in task_details['tasks']:
                    print(f"\nTask ARN: {task['taskArn']}")
                    print(f"Task Status: {task['lastStatus']}")
                    print(f"Health Status: {task.get('healthStatus', 'UNKNOWN')}")
                    
                    if 'containers' in task:
                        for container in task['containers']:
                            print(f"Container {container['name']}: {container['lastStatus']}")
            else:
                print("No tasks found")
        else:
            print("Service not found")
            
    except Exception as e:
        print(f"Error checking ECS service: {e}")
    
    print("\n=== Target Group Health ===")
    try:
        # Get target groups
        target_groups = elbv2.describe_target_groups(
            Names=['supplychain-tg']
        )
        
        if target_groups['TargetGroups']:
            tg_arn = target_groups['TargetGroups'][0]['TargetGroupArn']
            
            health = elbv2.describe_target_health(
                TargetGroupArn=tg_arn
            )
            
            print(f"Target Group ARN: {tg_arn}")
            for target in health['TargetHealthDescriptions']:
                print(f"Target: {target['Target']['Id']}:{target['Target']['Port']}")
                print(f"Health: {target['TargetHealth']['State']}")
                if 'Description' in target['TargetHealth']:
                    print(f"Description: {target['TargetHealth']['Description']}")
        else:
            print("Target group not found")
            
    except Exception as e:
        print(f"Error checking target group: {e}")
    
    print("\n=== Recent Logs ===")
    try:
        log_streams = logs.describe_log_streams(
            logGroupName='/ecs/supplychain',
            orderBy='LastEventTime',
            descending=True,
            limit=5
        )
        
        for stream in log_streams['logStreams']:
            print(f"\nLog Stream: {stream['logStreamName']}")
            
            events = logs.get_log_events(
                logGroupName='/ecs/supplychain',
                logStreamName=stream['logStreamName'],
                limit=10
            )
            
            for event in events['events'][-5:]:  # Last 5 events
                print(f"  {event['message'].strip()}")
                
    except Exception as e:
        print(f"Error checking logs: {e}")

if __name__ == "__main__":
    check_ecs_service()