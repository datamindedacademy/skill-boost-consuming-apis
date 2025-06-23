resource "aws_lb" "this" {
  name               = "skill-boost"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.lb.id]
  enable_deletion_protection = false
  subnets            = local.subnet_ids
}

resource "aws_lb_target_group" "this" {
  name        = "skill-boost"
  port        = 80
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = data.aws_vpc.default.id

  health_check {
    path                = "/"
    interval            = 30
    timeout             = 10
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }
}

resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.this.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-3-2021-06"
  certificate_arn   = aws_acm_certificate_validation.this.certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.this.arn
  }
}
