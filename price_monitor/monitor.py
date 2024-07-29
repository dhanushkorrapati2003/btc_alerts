import pika
import websocket
import json
import psycopg2
from psycopg2 import sql
import os

# RabbitMQ setup
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_QUEUE = 'alert_queue'

# PostgreSQL setup
DATABASE_SETTINGS = {
    'dbname': os.getenv('DATABASE_SETTINGS__DBNAME'),
    'user': os.getenv('DATABASE_SETTINGS__USER'),
    'password': os.getenv('DATABASE_SETTINGS__PASSWORD'),
    'host': os.getenv('DATABASE_SETTINGS__HOST'),
    'port': os.getenv('DATABASE_SETTINGS__PORT')
}

def push_to_rabbitmq(message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
    channel.basic_publish(exchange='', routing_key=RABBITMQ_QUEUE, body=json.dumps(message))
    connection.close()

def get_alerts_from_db():
    conn = psycopg2.connect(**DATABASE_SETTINGS)
    cur = conn.cursor(name='alert_cursor')  # Named cursor for streaming
    cur.execute("""
        SELECT id, target_price, trigger_condition, email, state
        FROM users_alert
        WHERE state = %s
    """, ('created',))
    
    # Stream alerts one by one
    while True:
        alert = cur.fetchone()
        if alert is None:
            break
        yield alert
    
    cur.close()
    conn.close()

def update_alert_state(alert_id, new_state):
    conn = psycopg2.connect(**DATABASE_SETTINGS)
    cur = conn.cursor()
    
    # Update alert state
    cur.execute("""
        UPDATE users_alert
        SET state = %s
        WHERE id = %s
    """, (new_state, alert_id))
    
    conn.commit()
    cur.close()
    conn.close()

def handle_price_update(price):
    for alert in get_alerts_from_db():
        alert_id, target_price, trigger_condition, email, state = alert
        if (trigger_condition == 'above' and price > target_price) or \
           (trigger_condition == 'below' and price < target_price):
            # Prepare the alert message
            alert_message = {
                'alert_id': alert_id,
                'target_price': str(target_price),
                'trigger_condition': trigger_condition,
                'price': price,
                'email' : email,
                'state' : state
            }
            # Push alert to RabbitMQ
            push_to_rabbitmq(alert_message)
            # Update alert state to 'triggered'
            update_alert_state(alert_id, 'triggered')

def on_message(ws, message):
    data = json.loads(message)
    price = data['data']['k']['c']
    if price is not None:
        handle_price_update(price)

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    print("WebSocket connection opened")

def run_websocket():
    websocket_url = "wss://stream.binance.com:9443/stream?streams=btcusdt@kline_1m"
    ws = websocket.WebSocketApp(websocket_url,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()

if __name__ == "__main__":
    run_websocket()
