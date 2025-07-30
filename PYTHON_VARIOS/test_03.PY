import requests
import pandas as pd

# Access token obtenido con Postman
access_token = '1000.0db40cf493836f3162321ace2197898d.25480934c23ca3ba2b6c72d9b5cd7193'
org_id = '707762349'
department_id = '123456789'  # Reemplaza este valor con el ID de tu departamento
per_page = 100
page = 1
ticket_data = []

headers = {
    'Authorization': f'Zoho-oauthtoken {access_token}',
    'orgId': org_id,
    'Content-Type': 'application/json'
}

# URL de los tickets archivados
url = 'https://desk.zoho.com/api/v1/tickets/archivedTickets'

# Bucle para paginar a través de todos los tickets archivados
while True:
    params = {
        'from': (page - 1) * per_page + 1,
        'limit': per_page,
        'departmentId': department_id  # Se agrega el ID del departamento
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        break

    tickets = response.json().get('data')

    if not tickets:
        break

    for ticket in tickets:
        ticket_number = ticket.get('ticketNumber')
        ticket_fecha = ticket.get('closedTime')
        ticket_estado = ticket.get('status')
        ticket_archivado = ticket.get('isArchived')
        ticket_ID = ticket.get('id')

        # Agregar ticket_ID a la lista
        ticket_data.append({
            'ticket_id': ticket_ID,
            'ticket_number': ticket_number,
            'ticket_fecha': ticket_fecha,
            'ticket_estado': ticket_estado,
            'ticket_archivado': ticket_archivado,
        })

    if len(tickets) < per_page:
        break

    page += 1


df = pd.DataFrame(ticket_data)


print(df)


df.to_csv('tickets_archivados.csv', index=False, encoding='utf-8')
