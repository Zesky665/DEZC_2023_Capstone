output "task_role" {
  description = "ECS Task Role"
  value       = aws_iam_role.prefect_agent_task_role.arn
}

output "execution_role" {
  description = "ECS Execution Role"
  value       = aws_iam_role.prefect_agent_execution_role.arn
}