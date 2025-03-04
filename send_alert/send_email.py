import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pika
import json
import os
    
def send_email(subject, body, to_email, from_email, smtp_server, smtp_port, smtp_user, smtp_password):
    # Create the email
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to the server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)

        # Send the email
        server.sendmail(from_email, to_email, msg.as_string())
        print(f"Email sent to {to_email}")

    except Exception as e:
        print(f"Failed to send email: {e}")
    finally:
        server.quit()

def callback(ch, method, properties, body):
    print("Received message from RabbitMQ")

    # Parse the message
    message = json.loads(body)
    subject = 'BTC Alert'
    body = 'Current price of BTC reached the target price ' + message['target_price']
    to_email = message['email']

    # SMTP server configuration
    smtp_server = 'smtp.google.com'
    smtp_port = 587
    smtp_user = 'user'
    smtp_password = 'password'
    from_email = 'alert@gmail.com'

    # Send the email
    send_email(subject, body, to_email, from_email, smtp_server, smtp_port, smtp_user, smtp_password)

def main():
    # RabbitMQ server configuration
    rabbitmq_host = os.getenv('RABBITMQ_HOST')
    rabbitmq_queue = os.getenv('RABBITMQ_QUEUE')

    # Connect to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
    channel = connection.channel()

    # Declare the queue
    channel.queue_declare(queue=rabbitmq_queue, durable=True)

    # Set up subscription on the queue
    channel.basic_consume(queue=rabbitmq_queue, on_message_callback=callback, auto_ack=True)

    print('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == "__main__":
    main()
