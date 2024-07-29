from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from users.models import Alert
from django.db.models import Q 

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_alert(request):
    target_price = request.data.get('target_price')
    trigger_condition = request.data.get('trigger_condition')
    email = request.data.get('email')

    if not target_price or not trigger_condition or not email:
        return JsonResponse({'error': 'Missing required fields'}, status=400)

    try:
        target_price = float(target_price)
    except ValueError:
        return JsonResponse({'error': 'Invalid target price'}, status=400)

    alert = Alert.objects.create(
        user=request.user,  # Automatically set the user
        target_price=target_price,
        trigger_condition=trigger_condition,
        email=email
    )

    return JsonResponse({'success': 'Alert created successfully', 'alert_id': alert.id})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_alert(request):
    alert_id = request.data.get('alert_id')

    if not alert_id:
        return JsonResponse({'error': 'Missing alert ID'}, status=400)

    try:
        alert = Alert.objects.get(id=alert_id)
        if alert.state == 'deleted':
            return JsonResponse({'error': 'Alert already deleted'}, status=400)
        alert.state = 'deleted'
        alert.save()
        return JsonResponse({'success': 'Alert marked as deleted'})
    except Alert.DoesNotExist:
        return JsonResponse({'error': 'Alert does not exist'}, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fetch_alerts(request):
    state = request.GET.get('state')

    filters = Q(user=request.user)  # Filter by the current logged-in user
    if state:
        if state not in ['created', 'triggered', 'deleted']:
            return JsonResponse({'error': 'Invalid state'}, status=400)
        filters &= Q(state=state)

    alerts = Alert.objects.filter(filters)

    alert_list = [
        {
            'id': alert.id,
            'target_price': str(alert.target_price),
            'trigger_condition': alert.trigger_condition,
            'email': alert.email,
            'state': alert.state
        }
        for alert in alerts
    ]

    return JsonResponse({'alerts': alert_list})
