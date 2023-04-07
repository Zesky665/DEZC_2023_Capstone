output "web_public_ip" {
    description     = "The public I address of the web server" 
    value           = aws_eip.capstone_web_eip.public_ip
    depends_on      = [aws_eip.capstone_web_eip]
}

output "web_public_dns" {
    description     = "The public DNS address of the web server"
    value           = aws_eip.capstone_web_eip.public_dns
    depends_on      = [aws_eip.capstone_web_eip]
}
