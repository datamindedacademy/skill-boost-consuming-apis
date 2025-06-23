data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

data "aws_subnet" "selected" {
  for_each = toset(data.aws_subnets.default.ids)
  id       = each.value
}

locals {
  availability_zones = distinct([for s in data.aws_subnet.selected : s.availability_zone])
  subnet_ids = [
    for az in local.availability_zones :
    (
      [for s in data.aws_subnet.selected : s.id if s.availability_zone == az][0]
    )
  ]
}

resource "aws_security_group" "lb" {
  name        = "skill-boost-lb-sg"
  description = "Allow HTTPS inbound traffic for the load balancer"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "HTTPS from anywhere"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "service" {
  name        = "skill-boost-service-sg"
  description = "Allow traffic from the load balancer"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description     = "Allow traffic from the load balancer"
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.lb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
