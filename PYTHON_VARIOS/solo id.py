import requests
import csv

# Access token obtenido con Postman
access_token = '1000.eec25ec3891065ff4a4f8ac6a7337ca8.3665c001bf1f3ff03141194db8f9b38f'
org_id = '707762349'  # org ID de Desk
per_page = 100
page = 1
ticket_numbers_list = []

headers = {
    'Authorization': f'Zoho-oauthtoken {access_token}',
    'orgId': org_id,
    'Content-Type': 'application/json'
}

#Bucle para paginar a través de todos los tickets disponibles
while True:
    params = {
        'from': (page - 1) * per_page + 1,
        'limit': per_page
    }
    # URL del endpoint desk.zoho.com/api/v1
    url = 'https://desk.zoho.com/api/v1/tickets'
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        break
    
    tickets = response.json().get('data')
    
    if not tickets:
        break
    
    # Encabezados que se necesitan ver
    for ticket in tickets:
        ticket_ID = ticket.get('id')
       # ticket_fecha = ticket.get('closedTime')
        #ticket_estado = ticket.get('status')
        #ticket_archivado = ticket.get('isArchived')
        #ticket_ID = ticket.get('id')

        ticket_numbers_list.append({
            'ticket_ID': ticket_ID,
         #   'ticket_fecha': ticket_fecha,
          #  'ticket_estado': ticket_estado,
           # 'ticket_archivado': ticket_archivado,
        })
    
    if len(tickets) < per_page:
        break
    
    page += 1

# Imprime los resultados en la consola
for ticket in ticket_numbers_list:
    print(f"TicketID: {ticket['ticket_ID']}")
       #  Estado: {ticket['ticket_estado']}, Hora de Cierre: {ticket['ticket_fecha']}, archivado: {ticket['ticket_archivado']}")

# Guardar en un archivo CSV
with open('tickets.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['ticket_number']
    #'ticket_estado', 'ticket_fecha', 'ticket_archivado']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for ticket in ticket_numbers_list:
        writer.writerow(ticket)

xd = pd